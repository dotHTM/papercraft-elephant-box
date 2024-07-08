from dataclasses import dataclass
from math import sqrt
from typing import Self


sqrt2over2 = sqrt(2) * 0.5


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, other: object) -> Self:
        if not isinstance(other, type(self)):
            raise NotImplementedError()
        return type(self)(
            self.x + other.x,
            self.y + other.y,
        )


def rotated_size(p1: Point, p2: Point) -> float:
    dx = abs(p2.x - p1.x)
    dy = abs(p2.y - p1.y)
    return (dx + dy) * sqrt2over2
