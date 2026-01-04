"""
Audio processing and transcription module.
Handles audio input (file paths or ComfyUI AUDIO tensors) and transcribes with word-level timestamps.
"""

import os
import tempfile
import numpy as np
import hashlib
import shutil
from typing import Tuple, List, Dict, Optional, Any

# Import logger
try:
    from .logger_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import cache manager
try:
    from .cache_manager import get_cache_manager
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    logger.warning("Cache manager not available, caching disabled")

try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

# Global model cache to avoid reloading models
_whisper_models = {}

try:
    import torch
    import torchaudio
    HAS_TORCHAUDIO = True
except ImportError:
    HAS_TORCHAUDIO = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


# Whisper model approximate sizes in MB (for disk space checking)
WHISPER_MODEL_SIZES = {
    "tiny": 75,
    "base": 150,
    "small": 500,
    "medium": 1500,
    "large": 3000,
    "large-v2": 3000,
    "large-v3": 3000,
}


def get_available_disk_space(path: str) -> float:
    """
    Get available disk space in MB for the given path.
    
    Args:
        path: Path to check disk space for
        
    Returns:
        Available space in MB, or -1 if unable to determine
    """
    try:
        stat = shutil.disk_usage(path)
        available_mb = stat.free / (1024 * 1024)
        return available_mb
    except Exception as e:
        logger.warning(f"Could not determine disk space for {path}: {e}")
        return -1


def get_model_size_mb(model_size: str) -> float:
    """
    Get approximate model size in MB.
    
    Args:
        model_size: Whisper model size string
        
    Returns:
        Approximate size in MB
    """
    return WHISPER_MODEL_SIZES.get(model_size.lower(), 3000)  # Default to large if unknown


def check_disk_space_for_model(model_size: str, cache_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if there's enough disk space to download the Whisper model.
    
    Args:
        model_size: Whisper model size
        cache_dir: HuggingFace cache directory (optional)
        
    Returns:
        Tuple of (has_space, error_message)
    """
    # Get model size
    model_size_mb = get_model_size_mb(model_size)
    
    # Determine cache directory
    if cache_dir is None:
        # Try to get HuggingFace cache directory
        cache_dir = os.path.expanduser("~/.cache/huggingface")
        if not os.path.exists(cache_dir):
            # Fallback to temp directory
            cache_dir = tempfile.gettempdir()
    
    # Check available space
    available_mb = get_available_disk_space(cache_dir)
    
    if available_mb < 0:
        # Can't determine space, allow attempt but warn
        logger.warning("Could not determine available disk space. Proceeding with model download...")
        return True, ""
    
    # Add 20% buffer for safety
    required_mb = model_size_mb * 1.2
    
    if available_mb < required_mb:
        # Suggest smaller models
        smaller_models = []
        for size, size_mb in sorted(WHISPER_MODEL_SIZES.items(), key=lambda x: x[1]):
            if size_mb < available_mb * 0.8:  # 80% of available space
                smaller_models.append(f"{size} (~{size_mb} MB)")
        
        error_msg = (
            f"Insufficient disk space to download Whisper model '{model_size}'.\n"
            f"  Required: ~{model_size_mb:.0f} MB\n"
            f"  Available: {available_mb:.0f} MB\n"
            f"  Cache location: {cache_dir}\n"
        )
        
        if smaller_models:
            error_msg += f"\nSuggested smaller models that fit:\n"
            for model in smaller_models:
                error_msg += f"  - {model}\n"
        else:
            error_msg += (
                f"\nNo Whisper models will fit in available space.\n"
                f"Please free up at least {required_mb - available_mb:.0f} MB of disk space."
            )
        
        return False, error_msg
    
    return True, ""


def process_audio_input(audio_input, temp_dir):
    """
    Extract audio from file path, AUDIO tensor, or ComfyUI AUDIO dict, save to temp file.
    
    Args:
        audio_input: Either a file path (str), ComfyUI AUDIO tensor, or ComfyUI AUDIO dict
        temp_dir: Temporary directory to save audio file
    
    Returns:
        Path to audio file
    """
    audio_path = os.path.join(temp_dir, "audio_input.wav")
    
    # Handle None
    if audio_input is None:
        return None
    
    # If it's a dict (ComfyUI AUDIO type format)
    if isinstance(audio_input, dict):
        logger.debug(f"Processing audio dict with keys: {audio_input.keys()}")
        
        # Check for file path in dict
        if "file_path" in audio_input:
            file_path = audio_input["file_path"]
            if isinstance(file_path, str) and os.path.exists(file_path):
                if file_path.lower().endswith('.wav'):
                    return file_path
                elif HAS_PYDUB:
                    audio = AudioSegment.from_file(file_path)
                    audio.export(audio_path, format="wav")
                    return audio_path
                else:
                    import shutil
                    shutil.copy(file_path, audio_path)
                    return audio_path
        
        # Check for audio tensor in dict (ComfyUI uses 'waveform' or 'audio')
        audio_tensor = None
        if "waveform" in audio_input:
            audio_tensor = audio_input["waveform"]
        elif "audio" in audio_input:
            audio_tensor = audio_input["audio"]
        
        if audio_tensor is not None and HAS_TORCHAUDIO:
            if isinstance(audio_tensor, torch.Tensor):
                # Get sample rate from dict or use default
                sample_rate = audio_input.get("sample_rate", 44100)
                
                # Handle tensor shapes
                if len(audio_tensor.shape) == 3:
                    audio_tensor = audio_tensor[0]  # [batch, channels, samples] -> [channels, samples]
                elif len(audio_tensor.shape) == 2:
                    pass  # Already [channels, samples]
                else:
                    raise ValueError(f"Unsupported audio tensor shape: {audio_tensor.shape}")
                
                # Convert to mono if stereo
                if audio_tensor.shape[0] > 1:
                    audio_tensor = audio_tensor.mean(dim=0, keepdim=True)
                
                # Validate and normalize audio tensor
                # Check for invalid values
                if torch.isnan(audio_tensor).any() or torch.isinf(audio_tensor).any():
                    logger.warning("Audio tensor contains NaN or Inf values. Clipping to valid range.")
                    audio_tensor = torch.nan_to_num(audio_tensor, nan=0.0, posinf=1.0, neginf=-1.0)
                
                # Ensure tensor is float32 (required by torchaudio)
                if audio_tensor.dtype != torch.float32:
                    audio_tensor = audio_tensor.to(torch.float32)
                
                # Normalize to [-1.0, 1.0] range if needed (torchaudio expects this range)
                audio_max = torch.abs(audio_tensor).max()
                if audio_max > 1.0:
                    logger.debug(f"Audio tensor values exceed [-1, 1] range (max: {audio_max:.3f}). Normalizing...")
                    audio_tensor = audio_tensor / audio_max
                elif audio_max == 0.0:
                    logger.warning("Audio tensor is all zeros. This may cause issues.")
                
                # Ensure sample rate is valid
                if sample_rate <= 0 or not isinstance(sample_rate, (int, float)):
                    logger.warning(f"Invalid sample rate: {sample_rate}. Using default 44100.")
                    sample_rate = 44100
                
                # Ensure tensor shape is correct: [channels, samples]
                if len(audio_tensor.shape) != 2:
                    raise ValueError(f"Audio tensor must be 2D [channels, samples], got shape: {audio_tensor.shape}")
                
                if audio_tensor.shape[0] == 0 or audio_tensor.shape[1] == 0:
                    raise ValueError(f"Audio tensor has invalid dimensions: {audio_tensor.shape}")
                
                logger.debug(f"Saving audio: shape={audio_tensor.shape}, dtype={audio_tensor.dtype}, sample_rate={sample_rate}")
                
                # Save using torchaudio
                try:
                    torchaudio.save(audio_path, audio_tensor, int(sample_rate))
                except Exception as e:
                    logger.error(f"Failed to save audio tensor: shape={audio_tensor.shape}, dtype={audio_tensor.dtype}, sample_rate={sample_rate}")
                    logger.error(f"Audio tensor stats: min={audio_tensor.min():.3f}, max={audio_tensor.max():.3f}, mean={audio_tensor.mean():.3f}")
                    raise RuntimeError(f"Failed to save audio file: {e}") from e
                
                return audio_path
        
        # If dict has a string value that looks like a path
        for key, value in audio_input.items():
            if isinstance(value, str) and os.path.exists(value):
                if value.lower().endswith('.wav'):
                    return value
                elif HAS_PYDUB:
                    audio = AudioSegment.from_file(value)
                    audio.export(audio_path, format="wav")
                    return audio_path
                else:
                    import shutil
                    shutil.copy(value, audio_path)
                    return audio_path
        
        raise ValueError(f"Audio dict does not contain valid audio data. Keys: {list(audio_input.keys())}")
    
    # If it's a string, assume it's a file path
    elif isinstance(audio_input, str):
        if os.path.exists(audio_input):
            # Convert to WAV if needed
            if audio_input.lower().endswith('.wav'):
                return audio_input
            elif HAS_PYDUB:
                # Convert using pydub
                audio = AudioSegment.from_file(audio_input)
                audio.export(audio_path, format="wav")
                return audio_path
            else:
                # Just copy if pydub not available
                import shutil
                shutil.copy(audio_input, audio_path)
                return audio_path
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_input}")
    
    # If it's a tensor (ComfyUI AUDIO type)
    elif HAS_TORCHAUDIO and isinstance(audio_input, torch.Tensor):
        # ComfyUI AUDIO tensor format: [batch, channels, samples] or [channels, samples]
        if len(audio_input.shape) == 3:
            # [batch, channels, samples] - take first batch
            audio_tensor = audio_input[0]
        elif len(audio_input.shape) == 2:
            # [channels, samples]
            audio_tensor = audio_input
        else:
            raise ValueError(f"Unsupported audio tensor shape: {audio_input.shape}")
        
        # Convert to mono if stereo
        if audio_tensor.shape[0] > 1:
            audio_tensor = audio_tensor.mean(dim=0, keepdim=True)
        
        # Ensure sample rate (default to 44100 if not specified)
        sample_rate = 44100
        
        # Save using torchaudio
        torchaudio.save(audio_path, audio_tensor, sample_rate)
        return audio_path
    
    else:
        raise ValueError(f"Unsupported audio input type: {type(audio_input)}. Expected dict, str, or torch.Tensor")


def transcribe_audio(audio_path: str, model_size: str = "base", language: str = "en") -> Tuple[Any, Any]:
    """
    Transcribe audio using faster-whisper with word-level timestamps.
    Results are cached based on audio file hash.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., "en", "es", "fr")
    
    Returns:
        Tuple of (segments, info) where segments contain word-level timestamps
    """
    if not HAS_WHISPER:
        error_msg = "faster-whisper is not installed. Please run: pip install faster-whisper"
        logger.error(error_msg)
        raise ImportError(error_msg)
    
    if not os.path.exists(audio_path):
        error_msg = f"Audio file not found: {audio_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Check cache first
    if HAS_CACHE:
        cache_manager = get_cache_manager()
        # Generate cache key from file hash and parameters
        with open(audio_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        cache_key = f"transcription_{file_hash}_{model_size}_{language}"
        
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            logger.info(f"Using cached transcription for {os.path.basename(audio_path)}")
            return cached_result['segments'], cached_result['info']
    
    logger.info(f"Transcribing audio: {os.path.basename(audio_path)} (model: {model_size}, language: {language})")
    
    # Determine device and compute type
    # Try to use GPU if available, fallback to CPU
    device = "cpu"
    compute_type = "int8"
    
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"  # Better performance on GPU
            logger.info("Using GPU for Whisper transcription")
        else:
            logger.info("GPU not available, using CPU for Whisper transcription")
    except ImportError:
        logger.warning("PyTorch not available, cannot detect GPU. Using CPU.")
    
    # Cache model instances to avoid reloading
    model_key = f"{model_size}_{device}_{compute_type}"
    if model_key not in _whisper_models:
        logger.info(f"Loading Whisper model: {model_size} on {device} ({compute_type})")
        
        # Check disk space before attempting download (warning only, don't block)
        # User may have space on other drives or the check might be inaccurate
        try:
            # Try to get HuggingFace cache directory from multiple sources
            cache_dir = None
            # Check environment variable first
            if "HF_HOME" in os.environ:
                cache_dir = os.path.join(os.environ["HF_HOME"], "hub")
            elif "HF_HUB_CACHE" in os.environ:
                cache_dir = os.environ["HF_HUB_CACHE"]
            else:
                # Try to get from huggingface_hub
                try:
                    import huggingface_hub
                    cache_dir = huggingface_hub.constants.HF_HUB_CACHE
                except (ImportError, AttributeError):
                    # Fallback to default location
                    cache_dir = os.path.expanduser("~/.cache/huggingface")
            
            # Check space but only warn, don't block
            has_space, error_msg = check_disk_space_for_model(model_size, cache_dir)
            if not has_space:
                logger.warning(f"Disk space check warning for model '{model_size}':")
                logger.warning(error_msg)
                logger.warning("Proceeding with download attempt anyway (check may be inaccurate or cache may be on different drive)")
        except Exception as e:
            logger.debug(f"Could not check disk space: {e}. Proceeding with download.")
        
        try:
            _whisper_models[model_key] = WhisperModel(
                model_size, 
                device=device, 
                compute_type=compute_type
            )
            logger.info("Whisper model loaded successfully")
        except OSError as e:
            # Check if it's a disk space error
            if "No space left on device" in str(e) or "Errno 28" in str(e):
                # Try to get actual cache directory for better error message
                try:
                    if "HF_HOME" in os.environ:
                        actual_cache = os.path.join(os.environ["HF_HOME"], "hub")
                    elif "HF_HUB_CACHE" in os.environ:
                        actual_cache = os.environ["HF_HUB_CACHE"]
                    else:
                        try:
                            import huggingface_hub
                            actual_cache = huggingface_hub.constants.HF_HUB_CACHE
                        except (ImportError, AttributeError):
                            actual_cache = os.path.expanduser("~/.cache/huggingface")
                except Exception:
                    actual_cache = "unknown"
                
                error_msg = (
                    f"Disk space error while downloading Whisper model '{model_size}'.\n"
                    f"  Model size: ~{get_model_size_mb(model_size):.0f} MB\n"
                    f"  Cache location: {actual_cache}\n"
                    f"\nSuggested solutions:\n"
                    f"  1. Free up disk space on the drive containing the cache\n"
                    f"  2. Change HuggingFace cache to a drive with more space:\n"
                    f"     - Set HF_HOME environment variable to a different location\n"
                    f"     - Or set HF_HUB_CACHE to a different location\n"
                    f"  3. Use a smaller model (tiny, base, small, or medium)\n"
                    f"  4. Clear old cached models from {actual_cache}"
                )
                logger.error(error_msg)
                raise OSError(error_msg) from e
            else:
                # Re-raise other OSErrors
                raise
    else:
        logger.debug(f"Reusing cached Whisper model: {model_key}")
    
    model = _whisper_models[model_key]
    
    # Transcribe with word timestamps
    logger.info("Starting transcription...")
    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language=language if language else None,
        beam_size=5  # Balance between speed and accuracy
    )
    logger.info("Transcription completed")
    
    # Convert generator to list for caching
    segments_list = list(segments)
    
    # Cache result
    if HAS_CACHE:
        cache_manager.set(cache_key, {
            'segments': segments_list,
            'info': info
        })
        logger.debug(f"Cached transcription result")
    
    return segments_list, info


def format_word_timestamps(segments):
    """
    Extract word-level timing data from Whisper segments.
    
    Args:
        segments: Whisper transcription segments
    
    Returns:
        List of dicts with word, start, end, and confidence
    """
    words = []
    
    for segment in segments:
        for word in segment.words:
            words.append({
                "word": word.word.strip(),
                "start": word.start,
                "end": word.end,
                "confidence": getattr(word, 'probability', 1.0)
            })
    
    return words


def get_audio_duration(audio_path):
    """
    Get duration of audio file in seconds.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Duration in seconds
    """
    if HAS_PYDUB:
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    elif HAS_TORCHAUDIO:
        info = torchaudio.info(audio_path)
        return info.num_frames / info.sample_rate
    else:
        # Fallback: try to get from transcription
        try:
            segments, info = transcribe_audio(audio_path, model_size="tiny")
            # Get last segment end time
            max_time = 0
            for segment in segments:
                if hasattr(segment, 'end'):
                    max_time = max(max_time, segment.end)
            return max_time
        except:
            raise RuntimeError("Cannot determine audio duration. Install pydub or torchaudio.")


def extract_audio_features(audio_path):
    """
    Extract basic audio features for animation synchronization.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Dict with audio features (duration, sample_rate, etc.)
    """
    features = {
        "duration": get_audio_duration(audio_path),
        "sample_rate": 44100,  # Default
    }
    
    if HAS_TORCHAUDIO:
        info = torchaudio.info(audio_path)
        features["sample_rate"] = info.sample_rate
        features["channels"] = info.num_channels
        features["num_frames"] = info.num_frames
    
    return features

