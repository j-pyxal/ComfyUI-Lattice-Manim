# Testing Documentation

## Current Testing Status

**⚠️ IMPORTANT**: The codebase uses relative imports (`.audio_processor`, `.caption_generator`, etc.) which only work when the module is imported as part of a package. This means:

1. **Tests cannot run directly** with `python test_node.py` - they will fail with `ImportError: attempted relative import with no known parent package`

2. **Tests must run in ComfyUI's context** where the package is properly loaded, OR

3. **Tests can be run as a package** using `python -m` from the parent directory

## What Has Been Tested

### ✅ Code Review & Static Analysis
- Removed duplicate class definitions
- Fixed timeline code generation
- Added JSON validation
- Added code syntax validation
- Fixed caption integration
- Improved error handling

### ⚠️ End-to-End Testing Status

**NOT YET TESTED** - The following need to be verified in a ComfyUI environment:

1. **Basic Manim Rendering**
   - ✅ Code structure is correct
   - ❌ Actual rendering not tested
   - ❌ File export format not verified

2. **Timeline Node**
   - ✅ JSON structure validated
   - ✅ Code generation logic reviewed
   - ❌ Actual timeline rendering not tested
   - ❌ Scene synchronization not verified

3. **Audio Processing**
   - ✅ Code structure reviewed
   - ❌ Audio transcription not tested
   - ❌ Word timestamp extraction not verified

4. **Caption Generation**
   - ✅ Code structure reviewed
   - ❌ Caption rendering not tested
   - ❌ Synchronization with audio not verified

5. **Export Format**
   - ✅ Tensor shape logic reviewed
   - ❌ Actual output format not verified
   - ❌ Value ranges not confirmed

## How to Test

### Option 1: Test in ComfyUI (Recommended)

1. Install the extension in ComfyUI:
   ```bash
   cd ComfyUI/custom_nodes
   git clone <repo-url> ComfyUI-Lattice-Manim
   cd ComfyUI-Lattice-Manim
   pip install -r requirements.txt
   ```

2. Start ComfyUI and test nodes in the UI

3. Check console output for errors

### Option 2: Manual Component Testing

Test individual components that don't require package imports:

```python
# Test timeline manager (no relative imports)
from timeline_scene_manager import TimelineSceneManager, SceneLayer

# Test code validator (no relative imports)
from code_validator import validate_manim_code

# Test presets (no relative imports)
from presets import ColorPresets, FontPresets
```

### Option 3: Integration Test Script

Create a test that runs within ComfyUI's Python environment:

```python
# This would run in ComfyUI's context
import sys
sys.path.insert(0, '/path/to/ComfyUI/custom_nodes/ComfyUI-Lattice-Manim')

from nodes import ManimScriptNode
# ... test code
```

## Known Issues to Test

1. **Timeline Code Generation**
   - Verify `play_timeline` integration works
   - Test fallback when `manim-play-timeline` not installed
   - Verify scene code executes at correct times

2. **Caption Integration**
   - Verify captions appear at correct times
   - Test word-by-word vs sentence modes
   - Verify font and color settings work

3. **Export Format**
   - Verify images are [Batch, Height, Width, Channels]
   - Verify values are normalized 0-1
   - Verify masks are all ones
   - Verify RGB vs BGR (should be RGB)

4. **Error Handling**
   - Test invalid JSON handling
   - Test empty timeline handling
   - Test code validation catches errors
   - Test missing dependencies

## Recommended Next Steps

1. **Create ComfyUI Integration Test**
   - Test within actual ComfyUI environment
   - Verify nodes appear in UI
   - Test basic rendering workflow

2. **Add Unit Tests for Isolated Components**
   - Test `timeline_scene_manager.py` (no relative imports)
   - Test `code_validator.py` (no relative imports)
   - Test `presets.py` (no relative imports)

3. **Add Mock Tests**
   - Mock Manim rendering
   - Mock audio processing
   - Test logic without full dependencies

4. **Manual Testing Checklist**
   - [ ] Basic Manim node renders correctly
   - [ ] Timeline node creates scenes
   - [ ] Audio transcription works
   - [ ] Captions appear synchronized
   - [ ] Export format is correct
   - [ ] Error messages are helpful

## Test Results Summary

**Status**: ⚠️ **PARTIALLY TESTED**

- ✅ Code structure and logic reviewed
- ✅ Critical bugs fixed
- ✅ Validation added
- ❌ End-to-end rendering not verified
- ❌ Export format not confirmed
- ❌ Integration with ComfyUI not tested

**Recommendation**: Test in actual ComfyUI environment before production use.

