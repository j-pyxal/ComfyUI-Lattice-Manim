"""
Manim code generation module.
Combines user code, captions, and presets into final Manim script.
"""

from .presets import ColorPresets, ShapePresets, EasingPresets, AnimationPresets
from .caption_generator import generate_caption_code


def build_manim_script(user_code, captions, audio_path, config):
    """
    Main builder function to create complete Manim script.
    
    Args:
        user_code: User's custom Manim code
        captions: Caption data (words with timestamps)
        audio_path: Path to audio file
        config: Configuration dict with all settings
    
    Returns:
        Complete Manim script as string
    """
    # Build header with config
    header = build_config_header(config)
    
    # Build caption code
    caption_code = ""
    if captions and config.get('enable_captions', True):
        caption_code = build_caption_section(captions, config)
    
    # Build shape animation code
    shape_code = ""
    if config.get('enable_shape_animations', True):
        shape_code = build_shape_animation_section(captions, config)
    
    # Build color animation code
    color_code = ""
    if config.get('enable_color_animations', False):
        color_code = build_color_animation_section(config)
    
    # Combine all parts - wrap in Scene class
    full_code = header
    
    # Start Scene class
    full_code += "\nclass CaptionedScene(Scene):\n"
    full_code += "    def construct(self):\n"
    
    # Indent all code blocks
    if caption_code:
        full_code += "        # === CAPTIONS ===\n"
        # Indent each line of caption code
        for line in caption_code.split("\n"):
            if line.strip():  # Skip empty lines
                full_code += "        " + line + "\n"
            else:
                full_code += "\n"
    
    if shape_code:
        full_code += "        # === SHAPE ANIMATIONS ===\n"
        for line in shape_code.split("\n"):
            if line.strip():
                full_code += "        " + line + "\n"
            else:
                full_code += "\n"
    
    if color_code:
        full_code += "        # === COLOR ANIMATIONS ===\n"
        for line in color_code.split("\n"):
            if line.strip():
                full_code += "        " + line + "\n"
            else:
                full_code += "\n"
    
    # Add user code (check if it's already in a class)
    if user_code.strip():
        # Check if user code already has a Scene class
        if "class" in user_code and "Scene" in user_code and "def construct" in user_code:
            # User code is complete, extract just the construct method content
            # Try to extract code from construct method
            if "def construct(self):" in user_code:
                construct_start = user_code.find("def construct(self):")
                construct_end = user_code.find("\n\n", construct_start)
                if construct_end == -1:
                    construct_end = len(user_code)
                construct_content = user_code[construct_start:construct_end]
                # Extract lines after "def construct(self):"
                lines = construct_content.split("\n")[1:]  # Skip method definition
                full_code += "        # === USER CODE ===\n"
                for line in lines:
                    if line.strip():
                        # Remove existing indentation and add our own
                        dedented = line.lstrip()
                        full_code += "        " + dedented + "\n"
                    else:
                        full_code += "\n"
            else:
                # Fallback: just add user code with indentation
                full_code += "        # === USER CODE ===\n"
                for line in user_code.split("\n"):
                    if line.strip():
                        dedented = line.lstrip()
                        full_code += "        " + dedented + "\n"
                    else:
                        full_code += "\n"
        else:
            # User code is not in a class, add it with indentation
            full_code += "        # === USER CODE ===\n"
            for line in user_code.split("\n"):
                if line.strip():
                    dedented = line.lstrip()
                    full_code += "        " + dedented + "\n"
                else:
                    full_code += "\n"
    
    return full_code


def build_config_header(config):
    """Build Manim configuration header"""
    width = config.get('width', 1920)
    height = config.get('height', 1080)
    frame_rate = config.get('frame_rate', 30)
    bg_color = config.get('background_color', 'BLACK')
    bg_color_hex = config.get('background_color_hex', None)
    
    header = f"""from manim import *
import numpy as np

# Configuration
config.pixel_width = {width}
config.pixel_height = {height}
config.frame_rate = {frame_rate}
"""
    
    if bg_color == 'CUSTOM' and bg_color_hex:
        header += f'config.background_color = "{bg_color_hex}"\n'
    else:
        header += f'config.background_color = {bg_color}\n'
    
    header += "\n"
    
    return header


def build_caption_section(captions, config):
    """Build caption rendering section"""
    caption_style = config.get('caption_style', 'word_by_word')
    position = config.get('caption_position', 'bottom')
    
    font_config = {
        'font': config.get('caption_font', 'Arial'),
        'size': config.get('caption_font_size', 48)
    }
    
    color_config = {
        'text_color': config.get('caption_color', 'WHITE'),
        'bg_color': config.get('caption_bg_color', 'TRANSPARENT')
    }
    
    # Generate caption code
    caption_code = generate_caption_code(
        captions, caption_style, position, font_config, color_config
    )
    
    return caption_code


def build_shape_animation_section(captions, config):
    """Build shape animation section synchronized with audio"""
    animation_type = config.get('shape_animation_type', 'auto')
    shape_preset = config.get('shape_preset', 'None')
    shape_color = config.get('shape_color', 'BLUE')
    easing = config.get('easing_function', 'smooth')
    
    code = ""
    
    if animation_type == 'auto' and captions:
        # Auto-generate based on word rhythm
        code = generate_auto_shape_animations(captions, shape_color, easing)
    elif shape_preset != 'None':
        # Use preset shape
        shapes = ShapePresets.get_3d_objects()
        if shape_preset in shapes:
            shape_code = shapes[shape_preset]
            # Replace color
            shape_code = shape_code.replace('BLUE', shape_color)
            code = f"""
# Preset shape: {shape_preset}
shape = {shape_code}
self.add(shape)
"""
            # Add animation based on type
            if animation_type == 'pulse':
                code += f"""
self.play(
    shape.animate.scale(1.2),
    rate_func={easing}
)
self.play(
    shape.animate.scale(1/1.2),
    rate_func={easing}
)
"""
            elif animation_type == 'rotate':
                code += f"""
self.play(
    Rotate(shape, PI/2),
    rate_func={easing}
)
"""
            elif animation_type == 'scale':
                code += f"""
self.play(
    shape.animate.scale(1.5),
    rate_func={easing}
)
"""
    else:
        # Default: simple circle pulse
        code = f"""
# Default shape animation
circle = Circle(radius=1, color={shape_color})
self.add(circle)

# Pulse animation
self.play(
    circle.animate.scale(1.3),
    rate_func={easing}
)
self.play(
    circle.animate.scale(1/1.3),
    rate_func={easing}
)
"""
    
    return code


def generate_auto_shape_animations(captions, shape_color, easing):
    """Generate shape animations based on word rhythm"""
    code = f"""
# Auto-generated shape animations based on audio rhythm
shapes = VGroup()

# Create shapes for each word
"""
    
    for i, word_data in enumerate(captions):
        word = word_data['word'].strip()
        if not word:
            continue
        
        start = word_data['start']
        end = word_data['end']
        duration = end - start
        
        # Create shape based on word length
        if len(word) < 4:
            shape_type = "Circle"
            shape_code = f"Circle(radius=0.3, color={shape_color})"
        elif len(word) < 7:
            shape_type = "Square"
            shape_code = f"Square(side_length=0.6, color={shape_color})"
        else:
            shape_type = "Polygon"
            shape_code = f"RegularPolygon(n=6, radius=0.4, color={shape_color})"
        
        code += f"""
# Word {i}: "{word}" - {shape_type}
shape_{i} = {shape_code}
shape_{i}.shift(RIGHT * {i * 0.8 - len(captions) * 0.4})
shapes.add(shape_{i})
"""
    
    code += """
self.add(shapes)

# Animate shapes appearing with words
"""
    
    for i, word_data in enumerate(captions):
        word = word_data['word'].strip()
        if not word:
            continue
        
        start = word_data['start']
        end = word_data['end']
        duration = end - start
        
        code += f"""
# Animate shape {i} for word "{word}"
self.play(
    GrowFromCenter(shapes[{i}]),
    run_time={duration:.3f},
    rate_func={easing}
)
"""
    
    return code


def build_color_animation_section(config):
    """Build color animation section"""
    anim_type = config.get('color_animation_type', 'rainbow')
    palette_name = config.get('color_palette', 'None')
    easing = config.get('easing_function', 'smooth')
    
    code = ""
    
    if palette_name != 'None':
        palettes = ColorPresets.get_color_palettes()
        colors = palettes.get(palette_name, [])
        
        if anim_type == 'rainbow':
            code = f"""
# Rainbow color animation
colors = {colors}
obj = Circle(radius=1)

for i, color in enumerate(colors):
    self.play(
        FadeToColor(obj, color),
        run_time=0.5,
        rate_func={easing}
    )
"""
        elif anim_type == 'gradient':
            code = f"""
# Gradient color animation
from manim import interpolate_color
colors = {colors}
obj = Circle(radius=1, color=colors[0])
self.add(obj)

for i in range(len(colors) - 1):
    self.play(
        obj.animate.set_color(
            interpolate_color(colors[i], colors[i+1], 1.0)
        ),
        run_time=0.5,
        rate_func={easing}
    )
"""
        elif anim_type == 'pulse':
            code = f"""
# Pulse color animation
obj = Circle(radius=1, color={colors[0] if colors else 'BLUE'})
self.add(obj)

for color in {colors}:
    self.play(
        obj.animate.set_color(color).scale(1.2),
        run_time=0.3,
        rate_func={easing}
    )
    self.play(
        obj.animate.scale(1/1.2),
        run_time=0.3,
        rate_func={easing}
    )
"""
    else:
        # Default rainbow cycle
        code = """
# Default rainbow animation
obj = Circle(radius=1)
colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

for color in colors:
    self.play(
        FadeToColor(obj, color),
        run_time=0.5
    )
"""
    
    return code


def inject_captions(base_code, caption_code, style):
    """Insert caption rendering code into base code"""
    # Find the construct method and inject captions
    if "def construct(self):" in base_code:
        # Insert after construct method start
        insert_pos = base_code.find("def construct(self):") + len("def construct(self):")
        # Find first line after construct
        next_line = base_code.find("\n", insert_pos)
        if next_line != -1:
            return base_code[:next_line+1] + caption_code + "\n" + base_code[next_line+1:]
    
    # If no construct method, add it
    return base_code + f"\n\nclass SceneWithCaptions(Scene):\n    def construct(self):\n{caption_code}\n"


def sync_animations_with_audio(animations, word_timestamps):
    """Synchronize animations with word timestamps"""
    synced = []
    
    for anim in animations:
        # Find closest word timestamp
        anim_time = anim.get('time', 0)
        closest_word = min(
            word_timestamps,
            key=lambda w: abs(w['start'] - anim_time)
        )
        
        anim['sync_time'] = closest_word['start']
        synced.append(anim)
    
    return synced

