"""
Simple end-to-end test that can run directly.
Tests actual rendering and file export functionality.
"""

import os
import sys
import json

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the relative imports for testing
import importlib
import types

# Create a mock module for relative imports
mock_module = types.ModuleType('mock_module')
sys.modules['mock_module'] = mock_module

# Try to import with package structure
try:
    # Change to package directory
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Import as package
    import nodes
    from timeline_scene_manager import TimelineSceneManager, SceneLayer
    from code_validator import validate_manim_code, validate_python_syntax
    
    print("✅ Imports successful")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nTo run tests properly:")
    print("1. Make sure you're in the project directory")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run: python -m pytest test_e2e_simple.py")
    sys.exit(1)
finally:
    os.chdir(original_dir)


def test_basic_manim_rendering():
    """Test basic Manim script node renders and exports frames"""
    print("\n=== Test 1: Basic Manim Rendering ===")
    
    node = nodes.ManimScriptNode()
    
    # Simple test code
    test_code = """
class TestScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle), run_time=1)
"""
    
    try:
        print("Rendering test scene (this may take 10-30 seconds)...")
        images, masks = node.render_manim(
            code=test_code,
            frame_count=30,
            width=512,
            height=512
        )
        
        # Verify output format
        assert isinstance(images, type(images)), "Images should be torch.Tensor"
        assert len(images.shape) == 4, f"Images should be 4D tensor, got {images.shape}"
        assert images.shape[1] == 512, f"Height should be 512, got {images.shape[1]}"
        assert images.shape[2] == 512, f"Width should be 512, got {images.shape[2]}"
        assert images.shape[3] == 3, f"Channels should be 3 (RGB), got {images.shape[3]}"
        assert images.shape[0] > 0, "Should have at least 1 frame"
        
        # Verify value range
        assert images.min() >= 0.0 and images.max() <= 1.0, "Image values should be normalized 0-1"
        
        # Verify mask
        assert masks.shape[:3] == images.shape[:3], "Mask shape should match image shape"
        
        print(f"✅ PASSED: Rendered {images.shape[0]} frames, shape {images.shape}")
        print(f"   Image dtype: {images.dtype}, range: [{images.min():.3f}, {images.max():.3f}]")
        print(f"   Mask dtype: {masks.dtype}, all ones: {(masks == 1.0).all()}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_validation():
    """Test code validation catches errors"""
    print("\n=== Test 2: Code Validation ===")
    
    # Test valid code
    valid_code = """
from manim import *

class Test(Scene):
    def construct(self):
        circle = Circle()
        self.add(circle)
"""
    is_valid, error = validate_manim_code(valid_code)
    assert is_valid, f"Valid code should pass: {error}"
    print("✅ Valid code passed validation")
    
    # Test invalid syntax
    invalid_syntax = """
from manim import *

class Test(Scene):
    def construct(self):
        circle = Circle(
        self.add(circle)
"""
    is_valid, error = validate_python_syntax(invalid_syntax)
    assert not is_valid, "Invalid syntax should fail"
    assert error is not None, "Should return error message"
    print("✅ Invalid syntax caught")
    
    # Test missing Manim import
    no_manim = """
class Test:
    def construct(self):
        pass
"""
    is_valid, error = validate_manim_code(no_manim)
    assert not is_valid, "Code without Manim import should fail"
    print("✅ Missing Manim import caught")
    
    return True


def test_timeline_auto_detection():
    """Test timeline auto-detection from word timestamps"""
    print("\n=== Test 3: Timeline Auto-Detection ===")
    
    # Create mock word timestamps
    word_timestamps = [
        {"word": "Hello", "start": 0.0, "end": 0.5},
        {"word": "world", "start": 0.5, "end": 1.0},
        {"word": ".", "start": 1.0, "end": 1.1},
        {"word": "This", "start": 1.5, "end": 1.8},
        {"word": "is", "start": 1.8, "end": 2.0},
        {"word": "a", "start": 2.0, "end": 2.1},
        {"word": "test", "start": 2.1, "end": 2.5},
        {"word": ".", "start": 2.5, "end": 2.6},
    ]
    
    manager = TimelineSceneManager(audio_duration=3.0)
    scenes = manager.auto_detect_scenes(word_timestamps, method="sentence")
    
    assert len(scenes) > 0, "Should detect at least one scene"
    assert scenes[0].start_time == 0.0, "First scene should start at 0.0"
    assert scenes[0].end_time >= 1.0, "First scene should end after first sentence"
    
    print(f"✅ PASSED: Auto-detected {len(scenes)} scenes")
    for i, scene in enumerate(scenes):
        print(f"   Scene {i+1}: {scene.start_time:.2f}s - {scene.end_time:.2f}s")
    
    return True


def test_timeline_json_roundtrip():
    """Test timeline JSON serialization/deserialization"""
    print("\n=== Test 4: Timeline JSON Roundtrip ===")
    
    manager = TimelineSceneManager(audio_duration=10.0)
    
    # Add some scenes
    scene1 = SceneLayer(1, 0.0, 3.0, "First scene", "auto", "code1")
    scene2 = SceneLayer(2, 3.0, 6.0, "Second scene", "auto", "code2")
    manager.add_scene(scene1)
    manager.add_scene(scene2)
    
    # Serialize
    json_str = manager.to_json()
    assert isinstance(json_str, str), "Should return JSON string"
    
    # Deserialize
    manager2 = TimelineSceneManager.from_json(json_str)
    assert len(manager2.layers) == 2, "Should have 2 scenes"
    assert manager2.layers[0].scene_id == 1, "First scene ID should be 1"
    assert manager2.layers[1].scene_id == 2, "Second scene ID should be 2"
    
    print("✅ PASSED: JSON roundtrip successful")
    print(f"   Serialized {len(manager.layers)} scenes")
    print(f"   Deserialized {len(manager2.layers)} scenes")
    
    return True


def test_export_format():
    """Test that exported files are in correct format"""
    print("\n=== Test 5: Export Format Verification ===")
    
    node = nodes.ManimScriptNode()
    
    test_code = """
class ExportTest(Scene):
    def construct(self):
        square = Square(color=RED)
        self.play(Create(square), run_time=1)
"""
    
    try:
        print("Rendering export test (this may take 10-30 seconds)...")
        images, masks = node.render_manim(
            code=test_code,
            frame_count=30,
            width=256,
            height=256
        )
        
        # Check tensor properties
        assert images.dtype.name == 'float32', f"Images should be float32, got {images.dtype}"
        assert masks.dtype.name == 'float32', f"Masks should be float32, got {masks.dtype}"
        
        # Check value range
        assert images.min() >= 0.0, "Image values should be >= 0"
        assert images.max() <= 1.0, "Image values should be <= 1"
        
        # Check shape consistency
        assert images.shape[0] == masks.shape[0], "Number of frames should match"
        assert images.shape[1] == masks.shape[1], "Height should match"
        assert images.shape[2] == masks.shape[2], "Width should match"
        
        print("✅ PASSED: Export format is correct")
        print(f"   Images: {images.shape}, dtype={images.dtype}")
        print(f"   Masks: {masks.shape}, dtype={masks.dtype}")
        print(f"   Value range: [{images.min():.3f}, {images.max():.3f}]")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all e2e tests"""
    print("=" * 60)
    print("ComfyUI Lattice Manim - End-to-End Tests")
    print("=" * 60)
    
    tests = [
        ("Code Validation", test_code_validation),
        ("Timeline Auto-Detection", test_timeline_auto_detection),
        ("Timeline JSON Roundtrip", test_timeline_json_roundtrip),
        ("Basic Manim Rendering", test_basic_manim_rendering),
        ("Export Format", test_export_format),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

