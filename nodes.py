import torch
import numpy as np
import cv2
import os
import subprocess
import tempfile

class ManimScriptNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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

    def render_manim(self, code, frame_count, width, height):
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
            
            # Write the script to file
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            # Build subprocess command
            output_name = "output"
            cmd = [
                "manim",
                "-ql",  # low quality for faster rendering
                "--disable_caching",
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
            
            # Check for output file (Manim creates output in various locations)
            # Search for .mp4 files recursively in temp_dir
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
                raise Exception(f"Manim rendering failed. Output file not found.\nLogs:\n{error_msg}")
            
            # Read video frames using OpenCV
            cap = cv2.VideoCapture(output_mp4)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Normalize to 0-1 float32
                frame_normalized = frame_rgb.astype(np.float32) / 255.0
                
                frames.append(frame_normalized)
            
            cap.release()
            
            if not frames:
                raise Exception("No frames extracted from Manim output video")
            
            # Stack frames into Torch Tensor: [Batch, Height, Width, Channels]
            frames_array = np.stack(frames, axis=0)
            image_tensor = torch.from_numpy(frames_array)
            
            # Create corresponding Mask Tensor: [Batch, Height, Width] (all ones)
            batch_size, h, w, _ = image_tensor.shape
            mask_tensor = torch.ones((batch_size, h, w), dtype=torch.float32)
            
            return (image_tensor, mask_tensor)
