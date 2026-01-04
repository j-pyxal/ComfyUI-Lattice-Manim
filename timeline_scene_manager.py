"""
Timeline scene management module.
Handles scene detection, layer management, and in/out frame control.
"""

from typing import List, Dict, Optional
import json


class SceneLayer:
    """Represents a single scene layer with in/out frames"""
    
    def __init__(self, scene_id: int, start_time: float, end_time: float,
                 prompt: str = "", visual_type: str = "auto",
                 manim_code: str = "", elements: List[Dict] = None):
        self.scene_id = scene_id
        self.start_time = start_time  # In point (seconds)
        self.end_time = end_time      # Out point (seconds)
        self.prompt = prompt
        self.visual_type = visual_type  # "auto", "shape", "data_viz", "custom"
        self.manim_code = manim_code
        self.elements = elements or []
        self.auto_generated = False
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "id": self.scene_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "prompt": self.prompt,
            "visual_type": self.visual_type,
            "manim_code": self.manim_code,
            "elements": self.elements,
            "auto_generated": self.auto_generated
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            scene_id=data.get("id", 0),
            start_time=data.get("start_time", 0.0),
            end_time=data.get("end_time", 0.0),
            prompt=data.get("prompt", ""),
            visual_type=data.get("visual_type", "auto"),
            manim_code=data.get("manim_code", ""),
            elements=data.get("elements", [])
        )
    
    def set_in_point(self, time: float):
        """Set the in point (start frame)"""
        self.start_time = max(0.0, min(time, self.end_time - 0.1))
    
    def set_out_point(self, time: float):
        """Set the out point (end frame)"""
        self.end_time = max(self.start_time + 0.1, time)
    
    def get_duration(self) -> float:
        """Get scene duration in seconds"""
        duration = self.end_time - self.start_time
        return max(0.01, duration)  # Ensure minimum duration for Manim


class TimelineSceneManager:
    """Manages timeline with multiple scene layers"""
    
    def __init__(self, audio_duration: float = 0.0):
        self.audio_duration = audio_duration
        self.layers: List[SceneLayer] = []
        self.next_scene_id = 1
    
    def auto_detect_scenes(self, word_timestamps: List[Dict], 
                          method: str = "sentence") -> List[SceneLayer]:
        """
        Auto-detect scenes from word timestamps.
        
        Args:
            word_timestamps: List of word dicts with 'word', 'start', 'end'
            method: 'sentence' (split on punctuation) or 'time' (fixed intervals)
        
        Returns:
            List of detected SceneLayer objects
        """
        scenes = []
        
        if method == "sentence":
            # Group words into sentences
            sentences = []
            current_sentence = []
            
            for word_data in word_timestamps:
                word = word_data['word'].strip()
                if not word:
                    continue
                
                current_sentence.append(word_data)
                
                # Check if word ends sentence
                if any(word.endswith(p) for p in ['.', '!', '?', ':', ';']):
                    if current_sentence:
                        sentences.append(current_sentence)
                        current_sentence = []
            
            # Add remaining words
            if current_sentence:
                sentences.append(current_sentence)
            
            # Create scenes from sentences
            for i, sentence_words in enumerate(sentences):
                if not sentence_words:
                    continue
                
                start_time = sentence_words[0]['start']
                end_time = sentence_words[-1]['end']
                sentence_text = ' '.join(w['word'].strip() for w in sentence_words)
                
                scene = SceneLayer(
                    scene_id=self.next_scene_id,
                    start_time=start_time,
                    end_time=end_time,
                    prompt=sentence_text,
                    visual_type="auto",
                    manim_code=""
                )
                scene.auto_generated = True
                scenes.append(scene)
                self.next_scene_id += 1
        
        elif method == "time":
            # Fixed time intervals (e.g., every 5 seconds)
            interval = 5.0
            current_time = 0.0
            
            while current_time < self.audio_duration:
                scene = SceneLayer(
                    scene_id=self.next_scene_id,
                    start_time=current_time,
                    end_time=min(current_time + interval, self.audio_duration),
                    prompt="",
                    visual_type="auto",
                    auto_generated=True
                )
                scenes.append(scene)
                self.next_scene_id += 1
                current_time += interval
        
        return scenes
    
    def add_scene(self, scene: SceneLayer):
        """Add a scene layer to the timeline"""
        scene.scene_id = self.next_scene_id
        self.next_scene_id += 1
        self.layers.append(scene)
        self.sort_layers()
    
    def remove_scene(self, scene_id: int):
        """Remove a scene by ID"""
        self.layers = [s for s in self.layers if s.scene_id != scene_id]
    
    def get_scene(self, scene_id: int) -> Optional[SceneLayer]:
        """Get scene by ID"""
        for scene in self.layers:
            if scene.scene_id == scene_id:
                return scene
        return None
    
    def update_scene(self, scene_id: int, **kwargs):
        """Update scene properties"""
        scene = self.get_scene(scene_id)
        if scene:
            for key, value in kwargs.items():
                if hasattr(scene, key):
                    setattr(scene, key, value)
    
    def sort_layers(self):
        """Sort layers by start time"""
        self.layers.sort(key=lambda s: s.start_time)
    
    def get_scenes_at_time(self, time: float) -> List[SceneLayer]:
        """Get all scenes active at a given time"""
        return [
            scene for scene in self.layers
            if scene.start_time <= time <= scene.end_time
        ]
    
    def to_json(self) -> str:
        """Export timeline to JSON"""
        data = {
            "audio_duration": self.audio_duration,
            "scenes": [scene.to_dict() for scene in self.layers]
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str):
        """Import timeline from JSON"""
        data = json.loads(json_str)
        manager = cls(audio_duration=data.get("audio_duration", 0.0))
        
        for scene_data in data.get("scenes", []):
            scene = SceneLayer.from_dict(scene_data)
            manager.layers.append(scene)
            manager.next_scene_id = max(manager.next_scene_id, scene.scene_id + 1)
        
        manager.sort_layers()
        return manager
    
    def generate_manim_timeline_code(self, frame_rate: int = 30, 
                                     word_timestamps: Optional[List[Dict]] = None,
                                     caption_config: Optional[Dict] = None) -> str:
        """
        Generate Manim code for timeline with all scenes.
        Uses manim-play-timeline for synchronized playback.
        
        Args:
            frame_rate: Frames per second
            word_timestamps: Optional word timestamps for captions
            caption_config: Optional caption configuration dict
        """
        code = """
from manim import *
try:
    from manim_play_timeline import play_timeline
    HAS_TIMELINE = True
except ImportError:
    HAS_TIMELINE = False
    print("Warning: manim-play-timeline not installed. Using sequential playback.")

class TimelineScene(Scene):
    def construct(self):
"""
        
        # If no timeline library, use sequential playback
        if not self.layers:
            code += "        # No scenes in timeline\n        pass\n"
            return code
        
        # Check if we should use timeline or sequential
        use_timeline = True
        try:
            import importlib
            importlib.import_module('manim_play_timeline')
        except ImportError:
            use_timeline = False
        
        if use_timeline:
            code += "        timeline = {}\n"
            
            # Add scenes to timeline
            for scene in self.layers:
                start_time_seconds = scene.start_time
                duration = scene.get_duration()
                
                # Generate scene code
                if scene.manim_code:
                    scene_code = scene.manim_code
                else:
                    # Ensure duration is positive
                    safe_duration = max(0.01, duration)
                    scene_code = f"""# Scene {scene.scene_id}: {scene.prompt[:50] if scene.prompt else 'Untitled'}
# Auto-generated placeholder
circle = Circle(radius=1, color=BLUE)
self.add(circle)
self.play(Create(circle), run_time={safe_duration:.2f})
"""
                
                # Create a function that executes the scene code
                # play_timeline will call this at the right time
                code += f"""
        # Scene {scene.scene_id} at {start_time_seconds:.2f}s
        def scene_{scene.scene_id}_exec():
{self._indent_code(scene_code, 12)}
        
        timeline[{start_time_seconds}] = scene_{scene.scene_id}_exec
"""
            
            # Captions will be added by the caller (nodes.py) to avoid circular imports
            
            code += """
        # Play timeline
        if HAS_TIMELINE:
            play_timeline(self, timeline)
        else:
            # Fallback: sequential playback
            for time_key in sorted(timeline.keys()):
                timeline[time_key]()
"""
        else:
            # Sequential playback fallback
            code += "        # Sequential scene playback (manim-play-timeline not available)\n"
            for scene in self.layers:
                duration = scene.get_duration()
                if scene.manim_code:
                    scene_code = scene.manim_code
                else:
                    scene_code = f"""# Scene {scene.scene_id}: {scene.prompt[:50] if scene.prompt else 'Untitled'}
circle = Circle(radius=1, color=BLUE)
self.add(circle)
self.play(Create(circle), run_time={duration:.2f})
"""
                code += f"\n        # Scene {scene.scene_id}\n"
                code += self._indent_code(scene_code, 8)
            
            # Captions will be added by the caller (nodes.py) to avoid circular imports
        
        return code
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces"""
        indent = " " * spaces
        lines = code.split("\n")
        result = []
        for line in lines:
            if line.strip():  # Only indent non-empty lines
                result.append(indent + line)
            else:
                result.append("")  # Keep empty lines empty
        return "\n".join(result)

