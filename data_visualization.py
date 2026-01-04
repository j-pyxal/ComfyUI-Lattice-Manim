"""
Data visualization generators for Manim.
Supports vector fields, time series, 3D plots, graphs, and particle systems.
"""

from .presets import ColorPresets


def generate_vector_field_code(data, function, config):
    """
    Create vector field from data or function.
    
    Args:
        data: Data structure (optional, if function provided)
        function: Python function/lambda for vector field
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    resolution = config.get('field_resolution', 20)
    streamlines = config.get('streamlines', False)
    
    if function:
        # Use provided function
        code = f"""
# Vector field from function
from manim import VectorField, StreamLines

def vector_func(pos):
    {function}
    return result

vector_field = VectorField(
    vector_func,
    x_range=[-7, 7, {resolution}],
    y_range=[-4, 4, {resolution}],
    length_func=lambda norm: 0.45 * sigmoid(norm)
)
self.add(vector_field)
"""
        if streamlines:
            code += """
stream_lines = StreamLines(
    vector_func,
    stroke_width=2,
    max_anchors_per_line=30
)
self.add(stream_lines)
stream_lines.start_animation(warm_up=False, flow_speed=1.5)
self.wait(stream_lines.virtual_time / stream_lines.flow_speed)
"""
    else:
        # Generate from data
        code = """
# Vector field from data
from manim import VectorField

# Vector field visualization
# Note: This is a placeholder implementation. For data-driven fields,
# extract vector data from input and map to field function.
# Example: Use numpy arrays or pandas DataFrames to generate field values.
vector_field = VectorField(
    lambda pos: pos,  # Placeholder: replace with data-driven function
    x_range=[-7, 7, 20],
    y_range=[-4, 4, 20]
)
self.add(vector_field)
"""
    
    return code


def generate_time_series_code(data, x_col, y_cols, config):
    """
    Generate time series visualization code.
    
    Args:
        data: Data structure with time series
        x_col: X column name
        y_cols: Y column names (comma-separated or list)
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    chart_type = config.get('chart_type', 'line')
    smooth_curve = config.get('smooth_curve', False)
    show_grid = config.get('show_grid', True)
    
    if isinstance(y_cols, str):
        y_cols = [col.strip() for col in y_cols.split(',')]
    
    code = f"""
# Time series visualization
from manim import Axes, Line, VGroup
import numpy as np

# Create axes
axes = Axes(
    x_range=[0, 10, 1],
    y_range=[0, 10, 1],
    x_length=10,
    y_length=6,
    axis_config={{"include_numbers": True}}
)
"""
    
    if show_grid:
        code += "axes.add_coordinates()\n"
    
    code += "self.add(axes)\n\n"
    
    if chart_type == 'line':
        code += """
# Line chart
lines = VGroup()
for y_col in y_cols:
    # Extract data for y_col
    # Note: Replace with actual data extraction from input
    # Example: if data is DataFrame, use data[x_col] and data[y_col]
    # For now using placeholder - implement based on actual data structure
    points = [(i, i**2/10) for i in range(11)]  # Placeholder - replace with actual data
    line = axes.plot_line_graph(
        x_values=[p[0] for p in points],
        y_values=[p[1] for p in points],
        add_vertex_dots=False
    )
    lines.add(line)

self.play(Create(lines))
"""
    elif chart_type == 'area':
        code += """
# Area chart
        # Area chart
        # Note: Area charts require filling under the curve
        # Use Manim's AreaUnderCurve or create custom filled polygon
        # Placeholder - implement based on data structure
        pass
"""
    elif chart_type == 'bar':
        code += """
# Bar chart
from manim import BarChart
bars = BarChart(
    values=[1, 2, 3, 4, 5],
    bar_names=["A", "B", "C", "D", "E"]
)
self.play(Create(bars))
"""
    
    return code


def generate_3d_scatter_code(data, x_col, y_col, z_col, color_col, config):
    """
    Generate 3D scatter plot code.
    
    Args:
        data: Data structure
        x_col: X column name
        y_col: Y column name
        z_col: Z column name
        color_col: Color column name (optional)
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    camera_angle = config.get('camera_angle', 45.0)
    enable_rotation = config.get('enable_rotation', True)
    
    code = f"""
# 3D scatter plot
from manim import ThreeDScene, Sphere, VGroup
import numpy as np

class Scatter3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi={camera_angle} * DEGREES, theta=45 * DEGREES)
        
        # Create scatter points
        points = VGroup()
        
        # Extract x, y, z data from data structure
        # Note: Implement based on actual data format (DataFrame, array, dict)
        # Example: if DataFrame, use data[x_col], data[y_col], data[z_col]
        # Placeholder - implement data extraction
        # Placeholder data
        for i in range(50):
            x = np.random.uniform(-3, 3)
            y = np.random.uniform(-3, 3)
            z = np.random.uniform(-3, 3)
            
            point = Sphere(radius=0.1, color=BLUE)
            point.move_to([x, y, z])
            points.add(point)
        
        self.add(points)
"""
    
    if enable_rotation:
        code += """
        # Rotate camera
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
"""
    
    return code


def generate_3d_surface_code(data, x_col, y_col, z_col, config):
    """
    Generate 3D surface plot code.
    
    Args:
        data: Data structure
        x_col: X column name
        y_col: Y column name
        z_col: Z column name
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    surface_type = config.get('surface_type', 'mesh')
    camera_angle = config.get('camera_angle', 45.0)
    
    code = f"""
# 3D surface plot
from manim import ThreeDScene, Surface, VGroup
import numpy as np

class Surface3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi={camera_angle} * DEGREES, theta=45 * DEGREES)
        
        # Create surface
        def surface_func(u, v):
            # TODO: Use actual data
            return np.array([
                u,
                v,
                np.sin(u) * np.cos(v)
            ])
        
        surface = Surface(
            surface_func,
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(20, 20)
        )
        
        self.add(surface)
"""
    
    return code


def generate_graph_code(nodes, edges, layout, config):
    """
    Generate graph/network visualization code.
    
    Args:
        nodes: List of node data
        edges: List of edge data
        layout: Layout algorithm name
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    layout_algorithm = config.get('layout_algorithm', 'spring')
    node_size_col = config.get('node_size_column', '')
    edge_weight_col = config.get('edge_weight_column', '')
    
    code = f"""
# Graph/network visualization
from manim import Graph, VGroup, Circle, Line
import networkx as nx

# Create NetworkX graph
G = nx.Graph()

# Add nodes
    # Add nodes from data
    # Note: Extract node data from input structure
    # Example: if DataFrame, iterate rows to create nodes
    # Placeholder - implement node creation from data
for i in range(10):
    G.add_node(i)

# Add edges
    # Add edges from data
    # Note: Extract edge data from input structure
    # Example: if DataFrame with source/target columns, create edges
    # Placeholder - implement edge creation from data
for i in range(9):
    G.add_edge(i, i+1)

# Create Manim graph
manim_graph = Graph(
    list(G.nodes()),
    list(G.edges()),
    layout="{layout_algorithm}",
    vertex_config={{"radius": 0.2, "color": BLUE}},
    edge_config={{"color": GRAY}}
)

self.play(Create(manim_graph))
"""
    
    return code


def generate_particle_system_code(particles, forces, config):
    """
    Generate particle system visualization code.
    
    Args:
        particles: Particle data
        forces: Force configuration
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    particle_count = config.get('particle_count', 100)
    force_type = config.get('force_type', 'gravity')
    particle_size = config.get('particle_size', 0.1)
    
    code = f"""
# Particle system
from manim import VGroup, Circle, Dot
import numpy as np

particles = VGroup()

# Create particles
for i in range({particle_count}):
    x = np.random.uniform(-5, 5)
    y = np.random.uniform(-3, 3)
    
    particle = Dot(point=[x, y, 0], radius={particle_size}, color=BLUE)
    particles.add(particle)

self.add(particles)

# Animate particles
def update_particles(particles, dt):
    # TODO: Implement force calculations
    for particle in particles:
        # Simple random motion
        particle.shift(np.random.uniform(-0.1, 0.1) * RIGHT + np.random.uniform(-0.1, 0.1) * UP)

particles.add_updater(update_particles)
self.wait(5)
particles.remove_updater(update_particles)
"""
    
    return code


def generate_visualization_code(vis_type, data_info, config):
    """
    Main function to generate visualization code based on type.
    
    Args:
        vis_type: Visualization type
        data_info: Processed data info dict
        config: Configuration dict
    
    Returns:
        Manim code string
    """
    if vis_type == 'vector_field':
        return generate_vector_field_code(
            data_info.get('data'),
            config.get('vector_field_function', ''),
            config
        )
    
    elif vis_type == 'time_series':
        return generate_time_series_code(
            data_info.get('data'),
            config.get('x_column', ''),
            config.get('y_columns', ''),
            config
        )
    
    elif vis_type == '3d_scatter':
        return generate_3d_scatter_code(
            data_info.get('data'),
            config.get('x_column', ''),
            config.get('y_column', ''),
            config.get('z_column', ''),
            config.get('color_column', ''),
            config
        )
    
    elif vis_type == '3d_surface':
        return generate_3d_surface_code(
            data_info.get('data'),
            config.get('x_column', ''),
            config.get('y_column', ''),
            config.get('z_column', ''),
            config
        )
    
    elif vis_type == 'graph_network':
        return generate_graph_code(
            config.get('nodes', []),
            config.get('edges', []),
            config.get('layout_algorithm', 'spring'),
            config
        )
    
    elif vis_type == 'particle_system':
        return generate_particle_system_code(
            config.get('particles', []),
            config.get('forces', {}),
            config
        )
    
    else:
        raise ValueError(f"Unknown visualization type: {vis_type}")

