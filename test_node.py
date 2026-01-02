from nodes import ManimScriptNode
import torch

# 1. Instantiate the node
node = ManimScriptNode()

# 2. Define a simple test script (A red square rotating)
test_code = """
class TestScene(Scene):
    def construct(self):
        sq = Square(color=RED, fill_opacity=1)
        self.play(Rotate(sq, PI/2), run_time=1)
"""

print("Rendering test scene... (This may take a few seconds)")

try:
    # 3. Run the render (Low res 512x512 for speed, 30 frames)
    images, masks = node.render_manim(test_code, frame_count=30, width=512, height=512)

    # 4. Verify output
    print(f"Success!")
    print(f"   Output Shape: {images.shape}")
    print(f"   Expected:     (30, 512, 512, 3)")
    
    if images.shape == (30, 512, 512, 3):
        print("   Status:       PASSED")
    else:
        print("   Status:       DIMENSION MISMATCH")

except Exception as e:
    print(f"Failed: {e}")

