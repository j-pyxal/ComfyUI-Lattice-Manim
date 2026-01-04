# ComfyUI Lattice Manim

A powerful ComfyUI custom node extension that integrates [Manim](https://www.manim.community/) for creating professional mathematical animations, data visualizations, and captioned videos directly within ComfyUI workflows.

## 🎯 Features

### Core Nodes

1. **ManimScriptNode** - Basic Manim rendering
   - Render custom Manim animations
   - Customizable resolution and frame count
   - Returns IMAGE and MASK tensors

2. **ManimAudioCaptionNode** - Audio-synchronized animations
   - Audio transcription with word-level timestamps
   - Automatic caption generation
   - Shape and color animations
   - Customizable caption styling

3. **ManimDataVisualizationNode** - Data-driven visualizations
   - Vector fields, time series, 3D plots
   - Graph/network visualizations
   - Particle systems
   - Supports CSV, JSON, NumPy, Pandas inputs

4. **ManimTimelineSceneNode** - Professional timeline editor
   - After Effects-style timeline with layers
   - Auto-detect scenes from audio transcription
   - Prompt-to-code generation (LLM or rule-based)
   - Visual timeline editor with in/out points
   - Full code editing capabilities

### Advanced Features

- **Audio Transcription**: Whisper-based transcription with word-level timestamps
- **Prompt-to-Code**: Generate Manim code from natural language descriptions
- **Timeline Management**: Scene-based editing with layer support
- **Caption Generation**: Word-by-word, sentence, or hybrid caption styles
- **Presets Library**: Colors, shapes, fonts, easing functions
- **Caching System**: Automatic caching of transcriptions and code generation
- **Code Validation**: Syntax checking before rendering
- **Comprehensive Logging**: Production-ready logging system

## 📦 Installation

1. Clone this repository into your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/j-pyxal/ComfyUI-Lattice-Manim.git
   cd ComfyUI-Lattice-Manim
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up OpenAI API key for LLM-based code generation:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   Or set it in your environment variables.

## 🚀 Usage

### Basic Manim Script Node

The `ManimScriptNode` accepts:
- **code**: Your Manim scene code (multiline string)
- **frame_count**: Number of frames to render (default: 30)
- **width**: Output width in pixels (default: 512)
- **height**: Output height in pixels (default: 512)

**Example:**
```python
class TestScene(Scene):
    def construct(self):
        sq = Square(color=RED, fill_opacity=1)
        self.play(Rotate(sq, PI/2), run_time=1)
```

### Audio Caption Node

The `ManimAudioCaptionNode` adds synchronized captions to your animations:
- Provide audio file or AUDIO tensor
- Automatic transcription with Whisper
- Word-by-word or sentence captions
- Customizable fonts, colors, and positions

### Timeline Scene Node

The `ManimTimelineSceneNode` provides professional timeline editing:

1. **Auto-Detection**: Automatically detects scenes from audio transcription
2. **Manual Editing**: Add, edit, or delete scenes with in/out points
3. **Prompt-to-Code**: Describe visuals in natural language, get Manim code
4. **Code Editing**: Full access to generated or custom Manim code
5. **Layer Management**: Multiple scenes with precise timing control

**Timeline JSON Format:**
```json
{
  "audio_duration": 30.5,
  "scenes": [
    {
      "id": 1,
      "start_time": 0.0,
      "end_time": 5.2,
      "prompt": "A blue circle rotating in the center",
      "visual_type": "auto",
      "manim_code": "circle = Circle(radius=1, color=BLUE)\nself.play(Rotate(circle, PI))",
      "auto_generated": true
    }
  ]
}
```

### Data Visualization Node

The `ManimDataVisualizationNode` creates visualizations from data:
- **Input**: CSV, JSON, NumPy arrays, or Pandas DataFrames
- **Types**: Vector fields, time series, 3D scatter/surface, graphs, particle systems
- **Customization**: Colors, animations, camera angles, and more

## 🎨 Presets

The extension includes extensive preset libraries:

- **Colors**: 71+ Manim colors and color palettes
- **Shapes**: 10+ 3D object presets
- **Fonts**: System font detection
- **Easing**: 18+ easing functions for animations

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY`: API key for LLM-based code generation (recommended)
- Cache directory: `~/.comfyui_lattice_manim_cache` (auto-created)

### Logging

The extension uses structured logging. Logs include:
- Timestamps
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Context information

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[IMPROVEMENTS.md](IMPROVEMENTS.md)** - Improvement recommendations
- **[TESTING.md](TESTING.md)** - Testing documentation
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - Implementation summary

## 🔧 Requirements

- Python 3.10+
- ComfyUI
- Manim (>=0.17.0,<0.18.0)
- NumPy (>=1.24.0,<2.0.0)
- OpenCV-Python (>=4.8.0,<5.0.0)
- faster-whisper (for audio transcription)
- Optional: OpenAI API (for LLM code generation)

See `requirements.txt` for complete dependency list with versions.

## 🎬 Example Workflows

### Creating a Captioned Video

1. Use `ManimAudioCaptionNode`
2. Provide audio file or AUDIO tensor
3. Configure caption style and appearance
4. Add custom Manim code for visuals
5. Render to get synchronized captioned video

### Timeline-Based Animation

1. Use `ManimTimelineSceneNode`
2. Provide audio for auto-detection OR manually create scenes
3. Add prompts for each scene (e.g., "A red square fading in")
4. Generate code automatically or edit manually
5. Adjust in/out points on timeline
6. Render final video

### Data Visualization

1. Use `ManimDataVisualizationNode`
2. Connect data input (CSV, JSON, etc.)
3. Select visualization type
4. Configure columns and styling
5. Render animated visualization

## 🐛 Troubleshooting

### Common Issues

**"Manim is not installed"**
- Run: `pip install manim`

**"faster-whisper is not installed"**
- Run: `pip install faster-whisper`

**API key not working**
- Set `OPENAI_API_KEY` environment variable
- Or provide in node parameter (less secure)

**Timeline not rendering**
- Check timeline JSON is valid
- Ensure scenes have valid start/end times
- Verify Manim code syntax

**Cache issues**
- Clear cache: Delete `~/.comfyui_lattice_manim_cache`
- Or use cache manager programmatically

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT

## 🙏 Acknowledgments

- [Manim Community](https://www.manim.community/) - Mathematical animation engine
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Node-based UI framework
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation

## 🔗 Links

- **Repository**: https://github.com/j-pyxal/ComfyUI-Lattice-Manim
- **Manim Documentation**: https://docs.manim.community/
- **ComfyUI Documentation**: https://github.com/comfyanonymous/ComfyUI

---

**Version**: 1.0.0  
**Last Updated**: 2024
