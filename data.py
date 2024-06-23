from dataclasses import dataclass
from typing import Dict

@dataclass
class Coordinate:
    x: int
    y: int

@dataclass
class Rectangle:
    lower_left: Coordinate
    lower_right: Coordinate
    upper_right: Coordinate
    upper_left: Coordinate

    @staticmethod
    def from_dict(data: Dict[str, int]) -> "Rectangle":
        return Rectangle(**data)

@dataclass
class Annotation:
    paper: Rectangle
    yellow_pen: Coordinate
    pink_pen: Coordinate
    orange_pen: Coordinate

    @staticmethod
    def from_dict(data: Dict[str, int]) -> "Annotation":
        return Annotation(**data)