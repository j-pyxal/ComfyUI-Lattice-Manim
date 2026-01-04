"""
Data input handling module.
Supports CSV, JSON, NumPy arrays, and Pandas DataFrames.
"""

import os
import json
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def load_data_from_file(file_path):
    """
    Load data from CSV or JSON file.
    
    Args:
        file_path: Path to CSV or JSON file
    
    Returns:
        Dict with 'data', 'type', 'columns', 'metadata'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.csv':
        return load_csv(file_path)
    elif ext in ['.json', '.jsonl']:
        return load_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def load_csv(file_path):
    """Load CSV file"""
    if HAS_PANDAS:
        df = pd.read_csv(file_path)
        return {
            'data': df,
            'type': 'dataframe',
            'columns': list(df.columns),
            'shape': df.shape,
            'metadata': {
                'dtypes': df.dtypes.to_dict(),
                'has_index': True
            }
        }
    else:
        # Fallback: read as plain text and parse manually
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            raise ValueError("Empty CSV file")
        
        # Parse header
        header = lines[0].strip().split(',')
        data = []
        for line in lines[1:]:
            if line.strip():
                values = line.strip().split(',')
                data.append(values)
        
        return {
            'data': np.array(data),
            'type': 'array',
            'columns': header,
            'shape': (len(data), len(header)),
            'metadata': {}
        }


def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Determine structure
    if isinstance(data, list):
        if HAS_PANDAS:
            df = pd.DataFrame(data)
            return {
                'data': df,
                'type': 'dataframe',
                'columns': list(df.columns) if len(df) > 0 else [],
                'shape': df.shape,
                'metadata': {}
            }
        else:
            # Convert to array
            if len(data) > 0 and isinstance(data[0], dict):
                # List of objects
                columns = list(data[0].keys())
                values = [[item.get(col) for col in columns] for item in data]
                return {
                    'data': np.array(values),
                    'type': 'array',
                    'columns': columns,
                    'shape': (len(values), len(columns)),
                    'metadata': {}
                }
            else:
                # List of values
                return {
                    'data': np.array(data),
                    'type': 'array',
                    'columns': ['value'],
                    'shape': (len(data), 1),
                    'metadata': {}
                }
    elif isinstance(data, dict):
        # Try to convert to DataFrame
        if HAS_PANDAS:
            df = pd.DataFrame([data])
            return {
                'data': df,
                'type': 'dataframe',
                'columns': list(df.columns),
                'shape': df.shape,
                'metadata': {}
            }
        else:
            return {
                'data': data,
                'type': 'dict',
                'columns': list(data.keys()),
                'shape': (1, len(data)),
                'metadata': {}
            }
    else:
        return {
            'data': data,
            'type': 'scalar',
            'columns': [],
            'shape': (1, 1),
            'metadata': {}
        }


def process_numpy_array(data):
    """
    Process NumPy array input.
    
    Args:
        data: NumPy array
    
    Returns:
        Dict with processed data info
    """
    if not isinstance(data, np.ndarray):
        raise ValueError(f"Expected NumPy array, got {type(data)}")
    
    shape = data.shape
    
    # Determine structure
    if len(shape) == 1:
        # 1D array
        columns = ['value']
        return {
            'data': data,
            'type': 'array_1d',
            'columns': columns,
            'shape': shape,
            'metadata': {}
        }
    elif len(shape) == 2:
        # 2D array (rows, columns)
        columns = [f'col_{i}' for i in range(shape[1])]
        return {
            'data': data,
            'type': 'array_2d',
            'columns': columns,
            'shape': shape,
            'metadata': {}
        }
    elif len(shape) == 3:
        # 3D array (for 3D plots)
        return {
            'data': data,
            'type': 'array_3d',
            'columns': ['x', 'y', 'z'],
            'shape': shape,
            'metadata': {}
        }
    else:
        raise ValueError(f"Unsupported array dimension: {len(shape)}")


def process_pandas_dataframe(df):
    """
    Process Pandas DataFrame.
    
    Args:
        df: Pandas DataFrame
    
    Returns:
        Dict with processed data info
    """
    if not HAS_PANDAS:
        raise ImportError("Pandas is required for DataFrame processing")
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"Expected DataFrame, got {type(df)}")
    
    return {
        'data': df,
        'type': 'dataframe',
        'columns': list(df.columns),
        'shape': df.shape,
        'metadata': {
            'dtypes': df.dtypes.to_dict(),
            'index_name': df.index.name,
            'has_index': True
        }
    }


def normalize_data(data, format='auto'):
    """
    Convert data to standard format for Manim.
    
    Args:
        data: Data in various formats
        format: Target format ('auto', 'array', 'dataframe')
    
    Returns:
        Normalized data structure
    """
    # Auto-detect format
    if format == 'auto':
        if isinstance(data, str):
            # File path
            return load_data_from_file(data)
        elif isinstance(data, np.ndarray):
            return process_numpy_array(data)
        elif HAS_PANDAS and isinstance(data, pd.DataFrame):
            return process_pandas_dataframe(data)
        else:
            raise ValueError(f"Cannot auto-detect format for {type(data)}")
    
    # Convert to specific format
    if format == 'array':
        if HAS_PANDAS and isinstance(data, pd.DataFrame):
            return {
                'data': data.values,
                'type': 'array',
                'columns': list(data.columns),
                'shape': data.shape,
                'metadata': {}
            }
        elif isinstance(data, np.ndarray):
            return process_numpy_array(data)
        else:
            raise ValueError(f"Cannot convert {type(data)} to array")
    
    elif format == 'dataframe':
        if not HAS_PANDAS:
            raise ImportError("Pandas required for DataFrame format")
        
        if isinstance(data, pd.DataFrame):
            return process_pandas_dataframe(data)
        elif isinstance(data, np.ndarray):
            df = pd.DataFrame(data)
            return process_pandas_dataframe(df)
        else:
            raise ValueError(f"Cannot convert {type(data)} to DataFrame")
    
    else:
        raise ValueError(f"Unknown format: {format}")


def detect_data_type(data):
    """
    Auto-detect data structure and type.
    
    Args:
        data: Data in various formats
    
    Returns:
        Dict with detected type and metadata
    """
    if isinstance(data, str):
        if os.path.exists(data):
            return {'type': 'file', 'path': data}
        else:
            return {'type': 'string', 'value': data}
    
    elif isinstance(data, np.ndarray):
        return {
            'type': 'numpy_array',
            'shape': data.shape,
            'dtype': str(data.dtype)
        }
    
    elif HAS_PANDAS and isinstance(data, pd.DataFrame):
        return {
            'type': 'dataframe',
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict()
        }
    
    elif isinstance(data, (list, tuple)):
        return {
            'type': 'list',
            'length': len(data),
            'element_type': type(data[0]).__name__ if data else 'unknown'
        }
    
    elif isinstance(data, dict):
        return {
            'type': 'dict',
            'keys': list(data.keys()),
            'length': len(data)
        }
    
    else:
        return {
            'type': 'unknown',
            'python_type': type(data).__name__
        }

