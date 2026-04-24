import json
import numpy as np
from typing import Dict, List

def grid_to_json(grid: np.ndarray) -> str:
    """Convert numpy grid to JSON string"""
    return json.dumps(grid.tolist())

def json_to_grid(json_str: str) -> np.ndarray:
    """Convert JSON string to numpy grid"""
    return np.array(json.loads(json_str))

def calculate_coverage(grid: np.ndarray) -> float:
    """Calculate coverage percentage from grid"""
    total = grid.size
    cleaned = np.count_nonzero(grid)
    return (cleaned / total) * 100 if total > 0 else 0

def compress_grid(grid: np.ndarray, compression_factor: int = 2) -> np.ndarray:
    """Compress grid for faster transmission"""
    h, w = grid.shape
    new_h, new_w = h // compression_factor, w // compression_factor
    compressed = np.zeros((new_h, new_w))

    for i in range(new_h):
        for j in range(new_w):
            compressed[i, j] = np.any(grid[
                i*compression_factor:(i+1)*compression_factor,
                j*compression_factor:(j+1)*compression_factor
            ])
    return compressed

def get_grid_statistics(grid: np.ndarray) -> Dict:
    """Get statistics about the grid"""
    cleaned = np.count_nonzero(grid)
    total = grid.size

    return {
        "total_cells": int(total),
        "cleaned_cells": int(cleaned),
        "uncleaned_cells": int(total - cleaned),
        "coverage_percent": float((cleaned / total) * 100) if total > 0 else 0.0
    }
