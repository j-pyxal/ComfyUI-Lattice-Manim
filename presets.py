"""
Preset library for Manim colors, shapes, fonts, easing functions, and animations.
"""

import platform
import os

try:
    import matplotlib.font_manager as fm
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ColorPresets:
    """Manim color presets and palettes"""
    
    @staticmethod
    def get_manim_colors():
        """Get all Manim predefined colors"""
        return [
            "WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW", "ORANGE",
            "PURPLE", "PINK", "GRAY", "GREY", "BROWN", "TEAL", "MAROON",
            "GOLD", "SILVER", "RED_A", "RED_B", "RED_C", "RED_D", "RED_E",
            "BLUE_A", "BLUE_B", "BLUE_C", "BLUE_D", "BLUE_E",
            "GREEN_A", "GREEN_B", "GREEN_C", "GREEN_D", "GREEN_E",
            "YELLOW_A", "YELLOW_B", "YELLOW_C", "YELLOW_D", "YELLOW_E",
            "ORANGE_A", "ORANGE_B", "ORANGE_C", "ORANGE_D", "ORANGE_E",
            "PURPLE_A", "PURPLE_B", "PURPLE_C", "PURPLE_D", "PURPLE_E",
            "PINK_A", "PINK_B", "PINK_C", "PINK_D", "PINK_E",
            "GRAY_A", "GRAY_B", "GRAY_C", "GRAY_D", "GRAY_E",
            "GREY_A", "GREY_B", "GREY_C", "GREY_D", "GREY_E",
            "BROWN_A", "BROWN_B", "BROWN_C", "BROWN_D", "BROWN_E",
            "TEAL_A", "TEAL_B", "TEAL_C", "TEAL_D", "TEAL_E",
        ]
    
    @staticmethod
    def get_color_palettes():
        """Predefined color palettes"""
        return {
            "Rainbow": ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "PURPLE"],
            "Sunset": ["#FF6B6B", "#FF8E53", "#FFA07A", "#FFB347", "#FFD700"],
            "Ocean": ["#001F3F", "#0074D9", "#39CCCC", "#7FDBFF", "#B2EBF2"],
            "Forest": ["#2D5016", "#3D7C47", "#5BA85B", "#7FB069", "#A8D5BA"],
            "Fire": ["#FF0000", "#FF4500", "#FF6347", "#FF8C00", "#FFA500"],
            "Ice": ["#E0F7FA", "#B2EBF2", "#80DEEA", "#4DD0E1", "#26C6DA"],
            "Neon": ["#FF00FF", "#00FFFF", "#FFFF00", "#FF00FF", "#00FF00"],
            "Pastel": ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"],
            "Monochrome": ["#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF"],
            "Vibrant": ["#FF1744", "#00E676", "#2196F3", "#FFC107", "#9C27B0"],
        }
    
    @staticmethod
    def hex_to_manim(hex_color):
        """Convert hex color to Manim color format"""
        return f'"{hex_color}"'
    
    @staticmethod
    def rgb_to_manim(r, g, b):
        """Convert RGB to Manim color format"""
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        return f'"{hex_color}"'


class ShapePresets:
    """3D and 2D shape presets"""
    
    @staticmethod
    def get_3d_objects():
        """Get 3D object presets"""
        return {
            "Sphere": "Sphere(radius=1, color=BLUE)",
            "Cube": "Cube(side_length=2, color=RED)",
            "Torus": "Torus(major_radius=1.5, minor_radius=0.5, color=GREEN)",
            "Cylinder": "Cylinder(radius=1, height=2, color=YELLOW)",
            "Cone": "Cone(base_radius=1, height=2, color=ORANGE)",
            "Prism": "Prism(dimensions=[1, 1, 1], color=PURPLE)",
            "Octahedron": "Octahedron(edge_length=1, color=TEAL)",
            "Icosahedron": "Icosahedron(edge_length=1, color=PINK)",
            "Dodecahedron": "Dodecahedron(edge_length=1, color=GOLD)",
            "TorusKnot": "TorusKnot(p=2, q=3, color=MAROON)",
        }
    
    @staticmethod
    def get_2d_shapes():
        """Get 2D shape presets"""
        return {
            "Circle": "Circle(radius=1, color=BLUE)",
            "Square": "Square(side_length=2, color=RED)",
            "Rectangle": "Rectangle(width=4, height=2, color=GREEN)",
            "Triangle": "Triangle(color=YELLOW)",
            "Polygon": "RegularPolygon(n=6, radius=1, color=PURPLE)",
            "Star": "Star(n=5, outer_radius=1, inner_radius=0.5, color=ORANGE)",
            "Ellipse": "Ellipse(width=4, height=2, color=PINK)",
            "Line": "Line(start=LEFT*2, end=RIGHT*2, color=WHITE)",
            "Arrow": "Arrow(start=LEFT*2, end=RIGHT*2, color=WHITE)",
        }


class FontPresets:
    """System font detection and management"""
    
    @staticmethod
    def get_system_fonts():
        """Detect available system fonts"""
        if not HAS_MATPLOTLIB:
            # Fallback to common fonts
            return [
                "Arial", "Times New Roman", "Courier New",
                "Helvetica", "Verdana", "Georgia", "Comic Sans MS"
            ]
        
        try:
            font_list = fm.findSystemFonts()
            font_names = []
            seen = set()
            
            for font_path in font_list:
                try:
                    font_prop = fm.FontProperties(fname=font_path)
                    font_name = font_prop.get_name()
                    if font_name and font_name not in seen:
                        font_names.append(font_name)
                        seen.add(font_name)
                except:
                    continue
            
            return sorted(font_names) if font_names else FontPresets.get_system_fonts.__defaults__[0]
        except Exception:
            # Fallback to common fonts
            return [
                "Arial", "Times New Roman", "Courier New",
                "Helvetica", "Verdana", "Georgia", "Comic Sans MS"
            ]


class EasingPresets:
    """Manim easing functions (rate functions)"""
    
    @staticmethod
    def get_easing_functions():
        """Get all Manim easing functions"""
        return [
            "linear",
            "smooth",
            "exponential_decay",
            "sine",
            "quadratic",
            "cubic",
            "quartic",
            "quintic",
            "exponential",
            "circular",
            "back",
            "elastic",
            "bounce",
            "there_and_back",
            "there_and_back_with_pause",
            "running_start",
            "not_quite_there",
            "wiggle",
        ]


class AnimationPresets:
    """Common animation templates"""
    
    @staticmethod
    def get_animation_presets():
        """Get animation preset templates"""
        return {
            "Fade In": "FadeIn(obj, rate_func={easing})",
            "Fade Out": "FadeOut(obj, rate_func={easing})",
            "Grow From Center": "GrowFromCenter(obj, rate_func={easing})",
            "Shrink To Center": "ShrinkToCenter(obj, rate_func={easing})",
            "Rotate": "Rotate(obj, PI/2, rate_func={easing})",
            "Scale Up": "obj.animate.scale(1.5).set_rate_func({easing})",
            "Scale Down": "obj.animate.scale(0.5).set_rate_func({easing})",
            "Move Left": "obj.animate.shift(LEFT*2).set_rate_func({easing})",
            "Move Right": "obj.animate.shift(RIGHT*2).set_rate_func({easing})",
            "Move Up": "obj.animate.shift(UP*2).set_rate_func({easing})",
            "Move Down": "obj.animate.shift(DOWN*2).set_rate_func({easing})",
        }
    
    @staticmethod
    def get_color_animation_templates():
        """Get color animation templates"""
        return {
            "Fade Between Colors": """
def animate_color_fade(obj, colors, duration=2):
    for i, color in enumerate(colors):
        self.play(FadeToColor(obj, color), run_time=duration/len(colors))
""",
            "Rainbow Cycle": """
def animate_rainbow(obj, duration=3):
    colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
    for color in colors:
        self.play(FadeToColor(obj, color), run_time=duration/len(colors))
""",
            "Gradient Shift": """
def animate_gradient(obj, colors, duration=2):
    from manim import interpolate_color
    for i in range(len(colors)-1):
        self.play(
            obj.animate.set_color(
                interpolate_color(colors[i], colors[i+1], 1.0)
            ),
            run_time=duration/(len(colors)-1)
        )
""",
            "Pulse": """
def animate_pulse(obj, color, duration=1):
    self.play(
        obj.animate.set_color(color).scale(1.2),
        run_time=duration/2
    )
    self.play(
        obj.animate.set_color(WHITE).scale(1/1.2),
        run_time=duration/2
    )
""",
        }

