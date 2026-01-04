"""
Audio processing and transcription module.
Handles audio input (file paths or ComfyUI AUDIO tensors) and transcribes with word-level timestamps.
"""

import os
import tempfile
import numpy as np
import hashlib
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
                
                # Save using torchaudio
                torchaudio.save(audio_path, audio_tensor, sample_rate)
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
    
    # Load Whisper model
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    # Transcribe with word timestamps
    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language=language if language else None
    )
    
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

