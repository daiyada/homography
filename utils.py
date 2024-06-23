from typing import Tuple

import numpy as np

from data import Rectangle, Coordinate

def get_rectangle_array(rect: Rectangle) -> np.ndarray:
    return np.array([
        (rect.lower_left.x, rect.lower_left.y),
        (rect.lower_right.x, rect.lower_right.y),
        (rect.upper_right.x, rect.upper_right.y),
        (rect.upper_left.x, rect.upper_left.y)
    ], dtype=np.float32)

def get_coord_tuple(coord: Coordinate, buffer: int = 0) -> Tuple[int, int]:
    return tuple([coord.x + buffer, coord.y + buffer])

def get_coord_array(coord: Coordinate, buffer: int = 0) -> np.ndarray:
    return np.array([coord.x, coord.y], dtype=np.float32) + buffer