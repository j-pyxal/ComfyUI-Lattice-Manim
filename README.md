# ComfyUI Lattice Manim

A ComfyUI custom node extension that integrates [Manim](https://www.manim.community/) for rendering mathematical animations directly within ComfyUI workflows.

## Features

- Render Manim animations as image sequences in ComfyUI
- Customizable resolution (width/height)
- Configurable frame count
- Returns both IMAGE and MASK tensors for downstream processing

## Installation

1. Clone this repository into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/j-pyxal/ComfyUI-Lattice-Manim.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The `ManimScriptNode` accepts:
- **code**: Your Manim scene code (multiline string)
- **frame_count**: Number of frames to render (default: 30)
- **width**: Output width in pixels (default: 1920)
- **height**: Output height in pixels (default: 1080)

### Example

```python
class TestScene(Scene):
    def construct(self):
        sq = Square(color=RED, fill_opacity=1)
        self.play(Rotate(sq, PI/2), run_time=1)
```

## Requirements

- Python 3.10+
- ComfyUI
- Manim
- NumPy
- OpenCV-Python

## License

MIT

