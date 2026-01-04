import torch
import numpy as np
import cv2
import os
import subprocess
import tempfile
from typing import Tuple, Optional, Dict, Any, List

from .audio_processor import process_audio_input, transcribe_audio, format_word_timestamps
from .caption_generator import generate_caption_code
from .manim_code_builder import build_manim_script
from .presets import ColorPresets, ShapePresets, FontPresets, EasingPresets
from .data_processor import normalize_data, detect_data_type
from .data_visualization import generate_visualization_code
from .timeline_scene_manager import TimelineSceneManager, SceneLayer
from .prompt_to_code import PromptToCodeGenerator
from .code_validator import validate_manim_code

# Import logger
try:
    from .logger_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Maximum safe number of frames to return (prevents memory issues)
# This is a starting point - actual limits are calculated dynamically
# based on resolution in extract_frames_from_video()
MAX_FRAMES_SAFE = 2000


def save_manim_frames(temp_dir: str) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Find and save Manim-rendered PNG frames to output directory.
    Manim renders frames to partial_movie_files directory.
    
    Args:
        temp_dir: Temporary directory where Manim rendered
    
    Returns:
        Tuple of (first_frame_tensor, mask_tensor) for preview
    """
    import shutil
    import time
    import glob
    
    # Find ComfyUI output directory
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        comfyui_root = os.path.dirname(os.path.dirname(current_dir))
        output_dir = os.path.join(comfyui_root, "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    except:
        output_dir = temp_dir
    
    # Manim stores frames in partial_movie_files directory
    # Search for PNG files in the temp directory
    frame_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith('.png'):
                frame_files.append(os.path.join(root, file))
    
    # Sort frames by name (Manim names them with frame numbers)
    frame_files.sort()
    
    if not frame_files:
        # Fallback: check for partial_movie_files directory
        partial_dir = os.path.join(temp_dir, "videos", "script")
        if os.path.exists(partial_dir):
            for root, dirs, files in os.walk(partial_dir):
                for file in files:
                    if file.endswith('.png'):
                        frame_files.append(os.path.join(root, file))
        frame_files.sort()
    
    if not frame_files:
        raise RuntimeError("No PNG frames found in Manim output. Manim may not have rendered frames correctly.")
    
    logger.info(f"Found {len(frame_files)} PNG frames from Manim")
    
    # Copy frames to output directory with sequential naming
    timestamp = int(time.time() * 1000)
    saved_frames = []
    for i, frame_path in enumerate(frame_files):
        output_filename = f"manim_frame_{timestamp}_{i:06d}.png"
        saved_frame_path = os.path.join(output_dir, output_filename)
        shutil.copy2(frame_path, saved_frame_path)
        saved_frames.append(saved_frame_path)
    
    logger.info(f"Saved {len(saved_frames)} frames to: {output_dir}")
    
    # Load first frame for preview
    first_frame_path = saved_frames[0]
    first_frame = cv2.imread(first_frame_path)
    if first_frame is None:
        raise RuntimeError(f"Failed to read first frame: {first_frame_path}")
    
    # Convert BGR to RGB and normalize
    frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
    frame_normalized = torch.from_numpy(frame_rgb.astype(np.float32) / 255.0)
    # Add batch dimension: [1, H, W, C]
    preview_tensor = frame_normalized.unsqueeze(0)
    
    # Create mask for single frame
    h, w, _ = preview_tensor.shape[1:]
    mask_tensor = torch.ones((1, h, w), dtype=torch.float32)
    
    return preview_tensor, mask_tensor


def extract_frames_from_video(video_path: str, max_frames: Optional[int] = None) -> Tuple[torch.Tensor, int, int]:
    """
    Extract frames from video file with automatic frame limiting to prevent memory issues.
    
    Args:
        video_path: Path to video file
        max_frames: Maximum frames to extract (defaults to MAX_FRAMES_SAFE)
    
    Returns:
        Tuple of (image_tensor, width, height)
    """
    if max_frames is None:
        max_frames = MAX_FRAMES_SAFE
    
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties first
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if total_frames == 0:
        cap.release()
        error_msg = "No frames extracted from Manim output video"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    # Calculate memory requirements
    estimated_memory_gb = total_frames * height * width * 3 * 4 / (1024**3)
    logger.info(f"Extracting {total_frames} frames ({width}x{height}) - estimated memory: {estimated_memory_gb:.2f} GB")
    
    # Additional safety: if single frame allocation would be too large, downscale resolution
    single_frame_mb = height * width * 3 * 4 / (1024**2)
    max_single_frame_mb = 50  # If a single frame is > 50MB, downscale
    
    original_width = width
    original_height = height
    
    if single_frame_mb > max_single_frame_mb:
        # Calculate downscale factor to get under limit
        scale_factor = (max_single_frame_mb / single_frame_mb) ** 0.5
        width = int(width * scale_factor)
        height = int(height * scale_factor)
        logger.warning(f"High resolution ({original_width}x{original_height}, {single_frame_mb:.1f} MB/frame) detected. Downscaling to {width}x{height} to prevent memory issues.")
        single_frame_mb = height * width * 3 * 4 / (1024**2)
    
    # Safety limit: warn and limit frames if output would be too large
    # Use a more reasonable limit based on resolution
    # For 1920x1080: ~23MB per frame, so 1000 frames = ~23GB (too much)
    # We'll use a dynamic limit: try to keep under 8GB for high-res, 2GB for lower res
    single_frame_gb = height * width * 3 * 4 / (1024**3)
    if single_frame_gb > 0.01:  # > 10MB per frame (high res)
        max_safe_memory_gb = 8.0  # Allow up to 8GB for high-res videos
    else:
        max_safe_memory_gb = 2.0  # 2GB for lower res
    
    estimated_limited_gb = max_frames * height * width * 3 * 4 / (1024**3)
    
    if estimated_limited_gb > max_safe_memory_gb:
        # Reduce frame count further if needed, but try to keep at least 300 frames
        calculated_max = int(max_safe_memory_gb * (1024**3) / (height * width * 3 * 4))
        max_frames = max(300, calculated_max)  # Minimum 300 frames (~10 seconds at 30fps)
        logger.warning(f"High resolution detected. Limiting to {max_frames} frames ({estimated_limited_gb:.2f} GB -> {max_frames * height * width * 3 * 4 / (1024**3):.2f} GB) to prevent memory issues.")
    
    if total_frames > max_frames:
        logger.warning(f"Video has {total_frames} frames, which would require {estimated_memory_gb:.2f} GB. Limiting to {max_frames} frames to prevent memory issues.")
        logger.warning(f"Consider using frame sampling or splitting long videos into segments.")
        # Sample frames evenly
        frame_skip = total_frames / max_frames
        target_frames = max_frames
    else:
        frame_skip = 1.0
        target_frames = total_frames
    
    # Final memory check before allocation
    final_memory_gb = target_frames * height * width * 3 * 4 / (1024**3)
    logger.info(f"Allocating {target_frames} frames at {width}x{height} - {final_memory_gb:.2f} GB")
    
    # Pre-allocate tensor to avoid memory spikes from list + stack
    try:
        image_tensor = torch.zeros((target_frames, height, width, 3), dtype=torch.float32)
    except RuntimeError as e:
        cap.release()  # Make sure to release before raising
        error_msg = f"Failed to allocate memory for {target_frames} frames at {width}x{height} ({final_memory_gb:.2f} GB). System may be out of memory."
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    frame_idx = 0
    output_idx = 0
    next_frame_to_keep = 0.0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Sample frames if needed
        if frame_idx >= next_frame_to_keep:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize if downscaled (check against original dimensions)
            if frame_rgb.shape[1] != width or frame_rgb.shape[0] != height:
                frame_rgb = cv2.resize(frame_rgb, (width, height), interpolation=cv2.INTER_AREA)
            
            # Normalize in one step
            frame_normalized = torch.from_numpy(frame_rgb.astype(np.float32) / 255.0)
            
            # Write directly to pre-allocated tensor
            image_tensor[output_idx] = frame_normalized
            output_idx += 1
            next_frame_to_keep += frame_skip
            
            # Stop if we've reached our limit
            if output_idx >= target_frames:
                break
        
        frame_idx += 1
        
        # Log progress for long videos
        if frame_idx % 100 == 0:
            logger.debug(f"Processed {frame_idx}/{total_frames} frames, extracted {output_idx}/{target_frames}...")
    
    # IMPORTANT: Release video capture BEFORE any other operations
    # This prevents file lock issues on Windows
    cap.release()
    
    # Trim to actual extracted frame count
    if output_idx < target_frames:
        image_tensor = image_tensor[:output_idx]
        logger.info(f"Adjusted frame count from {target_frames} to {output_idx}")
    
    logger.info(f"Successfully extracted {output_idx} frames (from {frame_idx} total frames in video)")
    
    return image_tensor, width, height


class ManimScriptNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s) -> Dict[str, Any]:
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "default": "class Example(Scene):\n    def construct(self):\n        c = Circle(color=BLUE)\n        self.play(Create(c))"}),
                "frame_count": ("INT", {"default": 30, "min": 1, "max": 1200}),
                "width": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "render_manim"
    CATEGORY = "Lattice/Experimental"

    def render_manim(self, code: str, frame_count: int, width: int, height: int) -> Tuple[torch.Tensor, torch.Tensor]:
        try:
            import manim
        except ImportError:
            raise ImportError("Manim is not installed. Please run pip install manim")
        
        # Create temporary directory for Manim output
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            
            # Prepend Manim config header to set pixel dimensions programmatically
            config_header = f"""from manim import *
config.pixel_width = {width}
config.pixel_height = {height}
config.frame_rate = 30

"""
            full_code = config_header + code
            
            # Validate code before rendering
            is_valid, validation_error = validate_manim_code(full_code)
            if not is_valid:
                raise ValueError(f"Manim code has syntax errors:\n{validation_error}")
            
            # Write the script to file
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            # Build subprocess command - render frames only (no video compilation)
            output_name = "output"
            cmd = [
                "manim",
                "-ql",  # low quality for faster rendering
                "--disable_caching",
                "--format", "png",  # Render as PNG frames
                "--media_dir", temp_dir,
                "-o", output_name,
                script_path
            ]
            
            # Execute Manim command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error("Manim rendering failed.")
                logger.debug(f"Manim stderr: {result.stderr}")
                logger.debug(f"Manim stdout: {result.stdout}")
                raise RuntimeError(f"Manim rendering failed.\nLogs:\n{error_msg}")
            
            # Save PNG frames and get preview
            preview_tensor, mask_tensor = save_manim_frames(temp_dir)
            
            return (preview_tensor, mask_tensor)


class ManimAudioCaptionNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        # Get dynamic lists from presets
        fonts = FontPresets.get_system_fonts()
        colors = ColorPresets.get_manim_colors()
        palettes = list(ColorPresets.get_color_palettes().keys())
        shapes = list(ShapePresets.get_3d_objects().keys())
        easing = EasingPresets.get_easing_functions()
        
        return {
            "required": {
                "code": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                # Audio input (either file path or AUDIO tensor)
                "audio": ("AUDIO", {"default": None}),
                "audio_file_path": ("STRING", {"default": "", "multiline": False}),
                
                # Audio/Transcription
                "whisper_model": (["tiny", "base", "small", "medium", "large"], {"default": "base"}),
                "language": ("STRING", {"default": "en"}),
                
                # Caption Configuration
                "enable_captions": ("BOOLEAN", {"default": True}),
                "caption_style": (["word_by_word", "sentence", "hybrid"], {"default": "word_by_word"}),
                "caption_position": (["bottom", "top", "center"], {"default": "bottom"}),
                "caption_font": (fonts if fonts else ["Arial"], {"default": fonts[0] if fonts else "Arial"}),
                "caption_font_size": ("INT", {"default": 48, "min": 12, "max": 200}),
                "caption_color": (colors, {"default": "WHITE"}),
                "caption_bg_color": (colors + ["TRANSPARENT"], {"default": "TRANSPARENT"}),
                
                # Shape Animations
                "enable_shape_animations": ("BOOLEAN", {"default": True}),
                "shape_animation_type": (["auto", "pulse", "rotate", "scale", "custom"], {"default": "auto"}),
                "shape_preset": (["None"] + shapes, {"default": "None"}),
                "shape_color": (colors, {"default": "BLUE"}),
                
                # Color Animations
                "enable_color_animations": ("BOOLEAN", {"default": False}),
                "color_animation_type": (["rainbow", "gradient", "pulse", "wave"], {"default": "rainbow"}),
                "color_palette": (["None"] + palettes, {"default": "None"}),
                
                # Easing
                "easing_function": (easing, {"default": "smooth"}),
                
                # Background
                "background_color": (colors + ["CUSTOM"], {"default": "BLACK"}),
                "background_color_hex": ("STRING", {"default": "#000000"}),
                
                # Rendering
                "width": ("INT", {"default": 1920, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 1080, "min": 64, "max": 4096}),
                "frame_rate": ("INT", {"default": 30, "min": 24, "max": 60}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "render_audio_captioned"
    CATEGORY = "Lattice/Enhanced"

    def render_audio_captioned(
        self, 
        code: str, 
        audio: Optional[Any] = None, 
        audio_file_path: str = "",
        whisper_model: str = "base", 
        language: str = "en",
        enable_captions: bool = True, 
        caption_style: str = "word_by_word",
        caption_position: str = "bottom", 
        caption_font: str = "Arial",
        caption_font_size: int = 48, 
        caption_color: str = "WHITE", 
        caption_bg_color: str = "TRANSPARENT",
        enable_shape_animations: bool = True, 
        shape_animation_type: str = "auto",
        shape_preset: str = "None", 
        shape_color: str = "BLUE",
        enable_color_animations: bool = False, 
        color_animation_type: str = "rainbow",
        color_palette: str = "None", 
        easing_function: str = "smooth",
        background_color: str = "BLACK", 
        background_color_hex: str = "#000000",
        width: int = 1920, 
        height: int = 1080, 
        frame_rate: int = 30
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        try:
            import manim
        except ImportError:
            raise ImportError("Manim is not installed. Please run pip install manim")
        
        # Process audio if provided
        captions = None
        audio_path = None
        
        if audio is not None or audio_file_path:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Process audio input
                if audio is not None:
                    audio_path = process_audio_input(audio, temp_dir)
                elif audio_file_path:
                    audio_path = process_audio_input(audio_file_path, temp_dir)
                
                if audio_path and enable_captions:
                    # Transcribe audio
                    segments, info = transcribe_audio(audio_path, whisper_model, language)
                    captions = format_word_timestamps(segments)
        
        # Build configuration
        config = {
            'width': width,
            'height': height,
            'frame_rate': frame_rate,
            'background_color': background_color,
            'background_color_hex': background_color_hex,
            'enable_captions': enable_captions,
            'caption_style': caption_style,
            'caption_position': caption_position,
            'caption_font': caption_font,
            'caption_font_size': caption_font_size,
            'caption_color': caption_color,
            'caption_bg_color': caption_bg_color,
            'enable_shape_animations': enable_shape_animations,
            'shape_animation_type': shape_animation_type,
            'shape_preset': shape_preset,
            'shape_color': shape_color,
            'enable_color_animations': enable_color_animations,
            'color_animation_type': color_animation_type,
            'color_palette': color_palette,
            'easing_function': easing_function,
        }
        
        # Build Manim script
        full_code = build_manim_script(code, captions, audio_path, config)
        
        # Render using existing logic
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            output_name = "output"
            cmd = [
                "manim",
                "-ql",
                "--disable_caching",
                "--media_dir", temp_dir,
                "-o", output_name,
                script_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Find output file
            output_mp4 = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.mp4'):
                        output_mp4 = os.path.join(root, file)
                        break
                if output_mp4:
                    break
            
            if not output_mp4:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error("Manim rendering failed. Output file not found.")
                logger.debug(f"Manim stderr: {result.stderr}")
                logger.debug(f"Manim stdout: {result.stdout}")
                raise RuntimeError(f"Manim rendering failed. Output file not found.\nLogs:\n{error_msg}")
            
            # Save PNG frames and get preview
            preview_tensor, mask_tensor = save_manim_frames(temp_dir)
            
            return (preview_tensor, mask_tensor)


class ManimDataVisualizationNode:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s) -> Dict[str, Any]:
        colors = ColorPresets.get_manim_colors()
        palettes = list(ColorPresets.get_color_palettes().keys())
        
        return {
            "required": {
                "data": ("*", {}),  # Accept any data type
                "visualization_type": ([
                    "vector_field",
                    "time_series",
                    "3d_scatter",
                    "3d_surface",
                    "graph_network",
                    "particle_system",
                    "custom"
                ], {"default": "time_series"}),
            },
            "optional": {
                # Data Configuration
                "data_format": (["auto", "csv", "json", "numpy", "pandas"], {"default": "auto"}),
                "x_column": ("STRING", {"default": ""}),
                "y_columns": ("STRING", {"default": ""}),
                "z_column": ("STRING", {"default": ""}),
                "color_column": ("STRING", {"default": ""}),
                
                # Vector Field Specific
                "vector_field_function": ("STRING", {"default": "", "multiline": True}),
                "streamlines": ("BOOLEAN", {"default": False}),
                "field_resolution": ("INT", {"default": 20, "min": 5, "max": 100}),
                
                # Time Series Specific
                "chart_type": (["line", "area", "bar", "candlestick"], {"default": "line"}),
                "smooth_curve": ("BOOLEAN", {"default": False}),
                "show_grid": ("BOOLEAN", {"default": True}),
                
                # 3D Plot Specific
                "surface_type": (["mesh", "wireframe", "solid"], {"default": "mesh"}),
                "camera_angle": ("FLOAT", {"default": 45.0, "min": 0, "max": 360}),
                "enable_rotation": ("BOOLEAN", {"default": True}),
                
                # Graph/Network Specific
                "layout_algorithm": (["spring", "circular", "hierarchical", "force_directed"], {"default": "spring"}),
                "node_size_column": ("STRING", {"default": ""}),
                "edge_weight_column": ("STRING", {"default": ""}),
                
                # Particle System Specific
                "particle_count": ("INT", {"default": 100, "min": 10, "max": 10000}),
                "force_type": (["gravity", "electromagnetic", "spring", "custom"], {"default": "gravity"}),
                "particle_size": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0}),
                
                # Animation
                "animate_data": ("BOOLEAN", {"default": True}),
                "animation_duration": ("FLOAT", {"default": 5.0, "min": 0.1, "max": 60.0}),
                
                # Styling
                "color_palette": (palettes, {"default": "Rainbow"}),
                "background_color": (colors, {"default": "BLACK"}),
                "enable_legend": ("BOOLEAN", {"default": True}),
                
                # Custom Code
                "custom_code": ("STRING", {"multiline": True, "default": ""}),
                
                # Rendering
                "width": ("INT", {"default": 1920, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 1080, "min": 64, "max": 4096}),
                "frame_rate": ("INT", {"default": 30, "min": 24, "max": 60}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "render_data_visualization"
    CATEGORY = "Lattice/Enhanced"

    def render_data_visualization(
        self, 
        data: Any, 
        visualization_type: str, 
        data_format: str = "auto",
        x_column: str = "", 
        y_columns: str = "", 
        z_column: str = "", 
        color_column: str = "",
        vector_field_function: str = "", 
        streamlines: bool = False, 
        field_resolution: int = 20,
        chart_type: str = "line", 
        smooth_curve: bool = False, 
        show_grid: bool = True,
        surface_type: str = "mesh", 
        camera_angle: float = 45.0, 
        enable_rotation: bool = True,
        layout_algorithm: str = "spring", 
        node_size_column: str = "", 
        edge_weight_column: str = "",
        particle_count: int = 100, 
        force_type: str = "gravity", 
        particle_size: float = 0.1,
        animate_data: bool = True, 
        animation_duration: float = 5.0,
        color_palette: str = "Rainbow", 
        background_color: str = "BLACK", 
        enable_legend: bool = True,
        custom_code: str = "", 
        width: int = 1920, 
        height: int = 1080, 
        frame_rate: int = 30
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        try:
            import manim
        except ImportError:
            raise ImportError("Manim is not installed. Please run pip install manim")
        
        # Process data
        data_info = normalize_data(data, data_format)
        
        # Build configuration
        config = {
            'width': width,
            'height': height,
            'frame_rate': frame_rate,
            'background_color': background_color,
            'x_column': x_column,
            'y_columns': y_columns,
            'z_column': z_column,
            'color_column': color_column,
            'vector_field_function': vector_field_function,
            'streamlines': streamlines,
            'field_resolution': field_resolution,
            'chart_type': chart_type,
            'smooth_curve': smooth_curve,
            'show_grid': show_grid,
            'surface_type': surface_type,
            'camera_angle': camera_angle,
            'enable_rotation': enable_rotation,
            'layout_algorithm': layout_algorithm,
            'node_size_column': node_size_column,
            'edge_weight_column': edge_weight_column,
            'particle_count': particle_count,
            'force_type': force_type,
            'particle_size': particle_size,
            'animate_data': animate_data,
            'animation_duration': animation_duration,
            'color_palette': color_palette,
            'enable_legend': enable_legend,
        }
        
        # Generate visualization code
        if visualization_type == "custom":
            vis_code = custom_code
        else:
            vis_code = generate_visualization_code(visualization_type, data_info, config)
        
        # Build complete script
        header = f"""from manim import *
import numpy as np

config.pixel_width = {width}
config.pixel_height = {height}
config.frame_rate = {frame_rate}
config.background_color = {background_color}

class DataVisualization(Scene):
    def construct(self):
{vis_code}
"""
        
        full_code = header
        
        # Validate code before rendering
        is_valid, validation_error = validate_manim_code(full_code)
        if not is_valid:
            raise ValueError(f"Generated Manim code has errors:\n{validation_error}")
        
        # Render
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            output_name = "output"
            cmd = [
                "manim",
                "-ql",
                "--disable_caching",
                "--media_dir", temp_dir,
                "-o", output_name,
                script_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Find output file
            output_mp4 = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.mp4'):
                        output_mp4 = os.path.join(root, file)
                        break
                if output_mp4:
                    break
            
            if not output_mp4:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error("Manim rendering failed. Output file not found.")
                logger.debug(f"Manim stderr: {result.stderr}")
                logger.debug(f"Manim stdout: {result.stdout}")
                raise RuntimeError(f"Manim rendering failed. Output file not found.\nLogs:\n{error_msg}")
            
            # Save PNG frames and get preview
            preview_tensor, mask_tensor = save_manim_frames(temp_dir)
            
            return (preview_tensor, mask_tensor)


class ManimTimelineSceneNode:
    """Timeline-based scene editor with prompt-to-code generation and layer management"""
    
    def __init__(self) -> None:
        pass
    
    @classmethod
    def INPUT_TYPES(s) -> Dict[str, Any]:
        fonts = FontPresets.get_system_fonts()
        colors = ColorPresets.get_manim_colors()
        
        return {
            "required": {
                "timeline_json": ("STRING", {"multiline": True, "default": "{}"}),
            },
            "optional": {
                # Audio input for auto-detection
                "audio": ("AUDIO", {"default": None}),
                "audio_file_path": ("STRING", {"default": "", "multiline": False}),
                
                # Auto-detection settings
                "auto_detect_scenes": ("BOOLEAN", {"default": True}),
                "detection_method": (["sentence", "time"], {"default": "sentence"}),
                
                # Transcription
                "whisper_model": (["tiny", "base", "small", "medium", "large"], {"default": "base"}),
                "language": ("STRING", {"default": "en"}),
                
                # Prompt-to-code generation
                "use_llm": ("BOOLEAN", {"default": True}),
                "llm_api_key": ("STRING", {"default": "", "multiline": False}),
                
                # Caption Configuration
                "enable_captions": ("BOOLEAN", {"default": True}),
                "caption_style": (["word_by_word", "sentence", "hybrid"], {"default": "word_by_word"}),
                "caption_position": (["bottom", "top", "center"], {"default": "bottom"}),
                "caption_font": (fonts if fonts else ["Arial"], {"default": fonts[0] if fonts else "Arial"}),
                "caption_font_size": ("INT", {"default": 48, "min": 12, "max": 200}),
                "caption_color": (colors, {"default": "WHITE"}),
                "caption_bg_color": (colors + ["TRANSPARENT"], {"default": "TRANSPARENT"}),
                
                # Background
                "background_color": (colors + ["CUSTOM"], {"default": "BLACK"}),
                "background_color_hex": ("STRING", {"default": "#000000"}),
                
                # Rendering
                "width": ("INT", {"default": 1920, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 1080, "min": 64, "max": 4096}),
                "frame_rate": ("INT", {"default": 30, "min": 24, "max": 60}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "timeline_json")
    FUNCTION = "render_timeline_scenes"
    CATEGORY = "Lattice/Enhanced"
    
    def render_timeline_scenes(self, timeline_json, audio=None, audio_file_path="",
                               auto_detect_scenes=True, detection_method="sentence",
                               whisper_model="base", language="en",
                               use_llm=True, llm_api_key="",
                               enable_captions=True, caption_style="word_by_word",
                               caption_position="bottom", caption_font="Arial",
                               caption_font_size=48, caption_color="WHITE",
                               caption_bg_color="TRANSPARENT",
                               background_color="BLACK", background_color_hex="#000000",
                               width=1920, height=1080, frame_rate=30):
        try:
            import manim
        except ImportError:
            raise ImportError("Manim is not installed. Please run pip install manim")
        
        # Initialize timeline manager
        audio_duration = 0.0
        word_timestamps = []
        
        # Process audio if provided
        if audio is not None or audio_file_path:
            with tempfile.TemporaryDirectory() as temp_dir:
                if audio is not None:
                    audio_path = process_audio_input(audio, temp_dir)
                elif audio_file_path:
                    audio_path = process_audio_input(audio_file_path, temp_dir)
                else:
                    audio_path = None
                
                if audio_path:
                    # Get audio duration
                    from .audio_processor import get_audio_duration
                    audio_duration = get_audio_duration(audio_path)
                    
                    # Transcribe if needed for auto-detection
                    if auto_detect_scenes:
                        segments, info = transcribe_audio(audio_path, whisper_model, language)
                        word_timestamps = format_word_timestamps(segments)
        
        # Load or create timeline with validation
        try:
            import json
            # Validate JSON structure
            if not timeline_json or timeline_json.strip() == "":
                timeline_json = "{}"
                logger.debug("Empty timeline JSON provided, creating new timeline")
            
            timeline_data = json.loads(timeline_json)
            if not isinstance(timeline_data, dict):
                error_msg = "Timeline JSON must be a dictionary"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            timeline_manager = TimelineSceneManager.from_json(timeline_json)
            timeline_manager.audio_duration = max(timeline_manager.audio_duration, audio_duration)
            logger.debug(f"Loaded timeline with {len(timeline_manager.layers)} scenes")
        except json.JSONDecodeError as e:
            error_msg = f"Invalid timeline JSON: {e}"
            logger.error(error_msg)
            logger.debug(f"JSON decode error details", exc_info=True)
            raise ValueError(error_msg)
        except (ValueError, KeyError, AttributeError) as e:
            # Create new timeline if parsing fails
            logger.warning(f"Failed to parse timeline JSON: {e}. Creating new timeline.")
            logger.debug(f"Timeline parsing error details", exc_info=True)
            timeline_manager = TimelineSceneManager(audio_duration=audio_duration)
        
        # Validate timeline has scenes
        if len(timeline_manager.layers) == 0:
            if auto_detect_scenes and word_timestamps:
                # Auto-detect scenes if enabled
                detected_scenes = timeline_manager.auto_detect_scenes(
                    word_timestamps, method=detection_method
                )
                for scene in detected_scenes:
                    timeline_manager.add_scene(scene)
            else:
                raise ValueError("Timeline has no scenes. Provide scenes in JSON or enable auto-detection with audio.")
        
        # Generate code for scenes that need it
        code_generator = PromptToCodeGenerator(use_llm=use_llm, llm_api_key=llm_api_key)
        
        for scene in timeline_manager.layers:
            if not scene.manim_code and scene.prompt:
                # Generate code from prompt
                try:
                    scene.manim_code = code_generator.generate_code(
                        scene.prompt,
                        visual_type=scene.visual_type
                    )
                    logger.debug(f"Generated code for scene {scene.scene_id}")
                except Exception as e:
                    logger.warning(f"Failed to generate code for scene {scene.scene_id}: {e}")
                    logger.debug(f"Code generation error details", exc_info=True)
                    # Use fallback placeholder
                    scene.manim_code = f"# Scene {scene.scene_id}: {scene.prompt}\ncircle = Circle(radius=1, color=BLUE)\nself.add(circle)"
        
        # Build complete Manim script
        timeline_code = timeline_manager.generate_manim_timeline_code(frame_rate)
        
        # Add captions if enabled - inject into the construct method
        if enable_captions and word_timestamps:
            from .caption_generator import generate_caption_code
            font_config = {
                'font': caption_font,
                'size': caption_font_size
            }
            color_config = {
                'text_color': caption_color,
                'bg_color': caption_bg_color
            }
            caption_code = generate_caption_code(
                word_timestamps, caption_style, caption_position,
                font_config, color_config
            )
            # Inject captions before the timeline playback
            # Find the last line before "play_timeline" or end of construct
            if "play_timeline(self, timeline)" in timeline_code:
                timeline_code = timeline_code.replace(
                    "        # Play timeline",
                    "        # === CAPTIONS ===\n" + 
                    "\n".join("        " + line for line in caption_code.split("\n")) + 
                    "\n        # Play timeline"
                )
            elif "timeline[time_key]()" in timeline_code:
                timeline_code = timeline_code.replace(
                    "            timeline[time_key]()",
                    "        # === CAPTIONS ===\n" + 
                    "\n".join("        " + line for line in caption_code.split("\n")) + 
                    "\n            timeline[time_key]()"
                )
            else:
                # Fallback: append at end of construct
                timeline_code = timeline_code.rstrip() + "\n        # === CAPTIONS ===\n"
                timeline_code += "\n".join("        " + line for line in caption_code.split("\n")) + "\n"
        
        # Build final script
        header = f"""from manim import *
import numpy as np

config.pixel_width = {width}
config.pixel_height = {height}
config.frame_rate = {frame_rate}
"""
        if background_color == "CUSTOM":
            header += f'config.background_color = "{background_color_hex}"\n'
        else:
            header += f'config.background_color = {background_color}\n'
        
        full_code = header + "\n" + timeline_code
        
        # Validate code before rendering
        is_valid, validation_error = validate_manim_code(full_code)
        if not is_valid:
            error_msg = f"Generated Manim code has errors:\n{validation_error}"
            logger.error(error_msg)
            logger.debug(f"Invalid code preview:\n{full_code[:500]}...")
            raise ValueError(f"{error_msg}\n\nCode preview:\n{full_code[:500]}...")
        
        # Render
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            output_name = "output"
            cmd = [
                "manim",
                "-ql",
                "--disable_caching",
                "--format", "png",  # Render as PNG frames
                "--media_dir", temp_dir,
                "-o", output_name,
                script_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error("Manim rendering failed.")
                logger.debug(f"Manim stderr: {result.stderr}")
                logger.debug(f"Manim stdout: {result.stdout}")
                raise RuntimeError(f"Manim rendering failed.\nLogs:\n{error_msg}")
            
            # Save PNG frames and get preview
            preview_tensor, mask_tensor = save_manim_frames(temp_dir)
            
            # Return updated timeline JSON
            updated_timeline_json = timeline_manager.to_json()
            
            return (preview_tensor, mask_tensor, updated_timeline_json)
