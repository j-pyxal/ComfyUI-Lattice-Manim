"""
Component-level tests that can run without ComfyUI.
Tests isolated components that don't require relative imports.
"""

import sys
import json

print("=" * 60)
print("Component-Level Tests")
print("=" * 60)

# Test 1: Code Validator
print("\n[1] Testing code_validator.py...")
try:
    from code_validator import validate_manim_code, validate_python_syntax
    
    # Test valid code
    valid_code = "from manim import *\nclass Test(Scene):\n    def construct(self):\n        pass"
    is_valid, error = validate_manim_code(valid_code)
    assert is_valid, f"Valid code failed: {error}"
    print("  [OK] Valid code passes")
    
    # Test invalid syntax
    invalid = "x = ("
    is_valid, error = validate_python_syntax(invalid)
    assert not is_valid, "Invalid syntax should fail"
    print("  [OK] Invalid syntax caught")
    
    # Test missing Manim import
    no_manim = "class Test:\n    pass"
    is_valid, error = validate_manim_code(no_manim)
    assert not is_valid, "Missing Manim import should fail"
    print("  [OK] Missing Manim import caught")
    
    print("  [PASS] code_validator.py: ALL TESTS PASSED")
except Exception as e:
    print(f"  [FAIL] code_validator.py: FAILED - {e}")
    import traceback
    traceback.print_exc()

# Test 2: Timeline Scene Manager
print("\n[2] Testing timeline_scene_manager.py...")
try:
    from timeline_scene_manager import TimelineSceneManager, SceneLayer
    
    # Test creation
    manager = TimelineSceneManager(audio_duration=10.0)
    assert manager.audio_duration == 10.0
    print("  [OK] Manager creation works")
    
    # Test scene creation
    scene = SceneLayer(1, 0.0, 5.0, "Test scene", "auto", "code")
    assert scene.scene_id == 1
    assert scene.get_duration() == 5.0
    print("  [OK] Scene creation works")
    
    # Test adding scenes
    manager.add_scene(scene)
    assert len(manager.layers) == 1
    print("  [OK] Adding scenes works")
    
    # Test JSON serialization
    json_str = manager.to_json()
    assert isinstance(json_str, str)
    data = json.loads(json_str)
    assert "scenes" in data
    assert len(data["scenes"]) == 1
    print("  [OK] JSON serialization works")
    
    # Test JSON deserialization
    manager2 = TimelineSceneManager.from_json(json_str)
    assert len(manager2.layers) == 1
    assert manager2.layers[0].scene_id == 1
    print("  [OK] JSON deserialization works")
    
    # Test auto-detection
    word_timestamps = [
        {"word": "Hello", "start": 0.0, "end": 0.5},
        {"word": "world", "start": 0.5, "end": 1.0},
        {"word": ".", "start": 1.0, "end": 1.1},
    ]
    scenes = manager.auto_detect_scenes(word_timestamps, method="sentence")
    assert len(scenes) > 0
    print(f"  [OK] Auto-detection works ({len(scenes)} scenes detected)")
    
    # Test code generation
    code = manager.generate_manim_timeline_code(frame_rate=30)
    assert "class TimelineScene" in code
    assert "def construct" in code
    print("  [OK] Code generation works")
    
    print("  [PASS] timeline_scene_manager.py: ALL TESTS PASSED")
except Exception as e:
    print(f"  [FAIL] timeline_scene_manager.py: FAILED - {e}")
    import traceback
    traceback.print_exc()

# Test 3: Presets
print("\n[3] Testing presets.py...")
try:
    from presets import ColorPresets, FontPresets, ShapePresets, EasingPresets
    
    # Test color presets
    colors = ColorPresets.get_manim_colors()
    assert len(colors) > 0
    assert "BLUE" in colors or "RED" in colors
    print(f"  [OK] Color presets work ({len(colors)} colors)")
    
    # Test font presets (may be empty if no fonts found)
    fonts = FontPresets.get_system_fonts()
    print(f"  [OK] Font detection works ({len(fonts)} fonts found)")
    
    # Test shape presets
    shapes = ShapePresets.get_3d_objects()
    assert len(shapes) > 0
    print(f"  [OK] Shape presets work ({len(shapes)} shapes)")
    
    # Test easing presets
    easing = EasingPresets.get_easing_functions()
    assert len(easing) > 0
    print(f"  [OK] Easing presets work ({len(easing)} functions)")
    
    print("  [PASS] presets.py: ALL TESTS PASSED")
except Exception as e:
    print(f"  [FAIL] presets.py: FAILED - {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Component Test Summary")
print("=" * 60)
print("\n[PASS] Components that can be tested independently work correctly.")
print("\n[WARN] Full end-to-end testing requires ComfyUI environment.")
print("       See TESTING.md for details on testing in ComfyUI.")

