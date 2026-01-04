"""
Code validation module for Manim scripts.
Validates Python syntax before rendering.
"""

import ast
import sys
from typing import Tuple, Optional


def validate_python_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python syntax of generated code.
    
    Args:
        code: Python code string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}: {e.msg}\n"
        if e.text:
            error_msg += f"  {e.text.strip()}\n"
            if e.offset:
                error_msg += "  " + " " * (e.offset - 1) + "^\n"
        return False, error_msg
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_manim_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Manim-specific code requirements.
    
    Args:
        code: Manim code string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # First check Python syntax
    is_valid, error = validate_python_syntax(code)
    if not is_valid:
        return False, error
    
    # Check for required Manim imports
    if "from manim import" not in code and "import manim" not in code:
        return False, "Missing Manim import. Code must include 'from manim import *' or 'import manim'"
    
    # Check for Scene class
    if "class" in code and "Scene" in code:
        # Check if construct method exists
        if "def construct" not in code:
            return False, "Scene class must have a 'construct' method"
    
    return True, None

