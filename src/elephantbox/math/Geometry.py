from __future__ import annotations

from collections.abc import Sequence
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

    def __mul__(self, other: object) -> Self:
        if isinstance(other, int) or isinstance(other, float):
            factor = float(other)
            return type(self)(
                self.x * factor,
                self.y * factor,
            )
        else:
            raise NotImplementedError()

    @property
    def tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def mirror_x(self) -> Self:
        return type(self)(-self.x, self.y)


def rotated_size(p1: Point, p2: Point) -> float:
    dx = abs(p2.x - p1.x)
    dy = abs(p2.y - p1.y)
    return (dx + dy) * sqrt2over2


def symetric_mirrored_summation_sequence(
    lengths: Sequence[float],
) -> list[float]:
    image = []
    acc = 0
    for length in lengths:
        acc += length
        image.append(acc)
    return [-i for i in reversed(image)] + image
