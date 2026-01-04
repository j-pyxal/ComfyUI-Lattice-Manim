"""
Prompt-to-code generation module.
Converts natural language prompts to Manim code using LLM or rule-based templates.
"""

import re
import os
from typing import Dict, Optional, Any
from .presets import ColorPresets, ShapePresets

# Try to import logger, fallback to print if not available
try:
    from .logger_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class PromptToCodeGenerator:
    """Generates Manim code from natural language prompts"""
    
    def __init__(self, use_llm: bool = True, llm_api_key: Optional[str] = None):
        self.use_llm = use_llm
        # Never store API key in plain text - use environment variable
        self._llm_api_key = None
        self.llm_client = None
        
        # Get API key from environment variable first, then parameter (masked)
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            self._llm_api_key = env_key
            logger.debug("Using OpenAI API key from environment variable")
        elif llm_api_key and llm_api_key.strip():
            # Warn about using parameter (less secure)
            logger.warning("API key provided as parameter. Consider using OPENAI_API_KEY environment variable instead.")
            self._llm_api_key = llm_api_key.strip()
        
        if use_llm:
            self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM client (OpenAI or compatible)"""
        try:
            import openai
            if self._llm_api_key:
                self.llm_client = openai.OpenAI(api_key=self._llm_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("No OpenAI API key found. LLM generation will be disabled.")
                self.use_llm = False
        except ImportError:
            self.use_llm = False
            logger.warning("OpenAI not installed. Falling back to rule-based generation.")
    
    def generate_code(self, prompt: str, visual_type: str = "auto",
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Manim code from prompt.
        Results are cached based on prompt hash.
        
        Args:
            prompt: Natural language description
            visual_type: Type of visualization ("auto", "shape", "data_viz", "custom")
            context: Additional context (colors, timing, etc.)
        
        Returns:
            Manim code string
        """
        # Check cache first
        try:
            from .cache_manager import get_cache_manager
            cache_manager = get_cache_manager()
            cache_key = f"code_gen_{hash(prompt)}_{visual_type}_{hash(str(context))}"
            cached_code = cache_manager.get(cache_key)
            if cached_code is not None:
                logger.debug(f"Using cached code generation for prompt: {prompt[:50]}...")
                return cached_code
        except ImportError:
            pass  # Cache not available, continue without it
        
        # Generate code
        if self.use_llm and self.llm_client:
            code = self._generate_with_llm(prompt, visual_type, context)
        else:
            code = self._generate_with_rules(prompt, visual_type, context)
        
        # Cache result
        try:
            cache_manager.set(cache_key, code)
        except:
            pass  # Cache failed, continue without it
        
        return code
    
    def _generate_with_llm(self, prompt: str, visual_type: str,
                          context: Optional[Dict]) -> str:
        """Generate code using LLM"""
        system_prompt = """You are a Manim code generator. Generate Python code for Manim animations based on natural language descriptions.

Rules:
1. Only generate the code inside the construct() method
2. Use Manim's standard classes: Scene, Circle, Square, Text, etc.
3. Include animations using self.play()
4. Use proper Manim syntax and imports
5. Keep code concise and focused on the described visual

Example:
Prompt: "A blue circle rotating in the center"
Code:
circle = Circle(radius=1, color=BLUE)
self.play(Create(circle))
self.play(Rotate(circle, PI), run_time=2)
"""
        
        user_prompt = f"Generate Manim code for: {prompt}"
        if context:
            user_prompt += f"\nContext: {context}"
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better quality
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            code = response.choices[0].message.content.strip()
            
            # Extract code block if present
            code = self._extract_code_block(code)
            
            return code
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}. Falling back to rule-based generation.")
            logger.debug(f"LLM error details", exc_info=True)
            return self._generate_with_rules(prompt, visual_type, context)
    
    def _generate_with_rules(self, prompt: str, visual_type: str,
                            context: Optional[Dict]) -> str:
        """Generate code using rule-based templates"""
        prompt_lower = prompt.lower()
        
        # Detect shapes
        shapes = {
            "circle": "Circle(radius=1, color={color})",
            "square": "Square(side_length=2, color={color})",
            "rectangle": "Rectangle(width=4, height=2, color={color})",
            "triangle": "Triangle(color={color})",
            "sphere": "Sphere(radius=1, color={color})",
            "cube": "Cube(side_length=2, color={color})",
        }
        
        # Detect colors
        colors = ColorPresets.get_manim_colors()
        detected_color = "BLUE"
        for color in colors:
            if color.lower() in prompt_lower:
                detected_color = color
                break
        
        # Detect animations
        animations = []
        if "rotate" in prompt_lower or "spinning" in prompt_lower:
            animations.append("Rotate(obj, PI, run_time=2)")
        if "fade" in prompt_lower or "appear" in prompt_lower:
            animations.append("FadeIn(obj)")
        if "scale" in prompt_lower or "grow" in prompt_lower:
            animations.append("obj.animate.scale(1.5)")
        if "move" in prompt_lower or "shift" in prompt_lower:
            if "left" in prompt_lower:
                animations.append("obj.animate.shift(LEFT*2)")
            elif "right" in prompt_lower:
                animations.append("obj.animate.shift(RIGHT*2)")
            elif "up" in prompt_lower:
                animations.append("obj.animate.shift(UP*2)")
            elif "down" in prompt_lower:
                animations.append("obj.animate.shift(DOWN*2)")
        
        # Detect shape
        detected_shape = "Circle"
        shape_code = shapes.get("circle", "Circle(radius=1, color={color})")
        for shape_name, shape_template in shapes.items():
            if shape_name in prompt_lower:
                detected_shape = shape_name.capitalize()
                shape_code = shape_template
                break
        
        # Generate code
        code = f"""
# Generated from prompt: "{prompt}"
obj = {shape_code.format(color=detected_color)}

# Position
if "center" in "{prompt_lower}":
    obj.move_to(ORIGIN)
elif "left" in "{prompt_lower}":
    obj.to_edge(LEFT)
elif "right" in "{prompt_lower}":
    obj.to_edge(RIGHT)
elif "top" in "{prompt_lower}":
    obj.to_edge(UP)
elif "bottom" in "{prompt_lower}":
    obj.to_edge(DOWN)
else:
    obj.move_to(ORIGIN)

self.add(obj)
"""
        
        # Add animations
        if animations:
            code += "\n# Animations\n"
            for anim in animations:
                code += f"self.play({anim})\n"
        else:
            code += "self.play(Create(obj))\n"
        
        return code
    
    def _extract_code_block(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        # Remove ```python or ``` markers
        text = re.sub(r'```python?\n?', '', text)
        text = re.sub(r'```\n?', '', text)
        return text.strip()
    
    def refine_code(self, prompt: str, existing_code: str, 
                   feedback: str) -> str:
        """
        Refine existing code based on feedback.
        
        Args:
            prompt: Original prompt
            existing_code: Current Manim code
            feedback: User feedback (e.g., "make it bigger", "change color to red")
        
        Returns:
            Refined Manim code
        """
        if self.use_llm and self.llm_client:
            return self._refine_with_llm(prompt, existing_code, feedback)
        else:
            return self._refine_with_rules(existing_code, feedback)
    
    def _refine_with_llm(self, prompt: str, existing_code: str,
                        feedback: str) -> str:
        """Refine code using LLM"""
        system_prompt = """You are a Manim code refiner. Modify existing Manim code based on user feedback.

Keep the structure but apply the requested changes."""
        
        user_prompt = f"""Original prompt: {prompt}

Current code:
{existing_code}

User feedback: {feedback}

Provide the refined code:"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            code = response.choices[0].message.content.strip()
            return self._extract_code_block(code)
        except Exception as e:
            logger.warning(f"LLM refinement failed: {e}. Falling back to rule-based refinement.")
            logger.debug(f"LLM refinement error details", exc_info=True)
            return self._refine_with_rules(existing_code, feedback)
    
    def _refine_with_rules(self, existing_code: str, feedback: str) -> str:
        """Refine code using simple rule-based modifications"""
        code = existing_code
        feedback_lower = feedback.lower()
        
        # Color changes
        colors = ColorPresets.get_manim_colors()
        for color in colors:
            if color.lower() in feedback_lower:
                code = re.sub(r'color=\w+', f'color={color}', code)
                break
        
        # Size changes
        if "bigger" in feedback_lower or "larger" in feedback_lower:
            code = re.sub(r'radius=(\d+)', lambda m: f'radius={float(m.group(1)) * 1.5}', code)
            code = re.sub(r'side_length=(\d+)', lambda m: f'side_length={float(m.group(1)) * 1.5}', code)
        elif "smaller" in feedback_lower:
            code = re.sub(r'radius=(\d+)', lambda m: f'radius={float(m.group(1)) * 0.7}', code)
            code = re.sub(r'side_length=(\d+)', lambda m: f'side_length={float(m.group(1)) * 0.7}', code)
        
        return code

