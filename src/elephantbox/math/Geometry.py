from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import atan2
from math import cos
from math import pi
from math import sin
from math import sqrt
from typing import Self


sqrt2over2 = sqrt(2) * 0.5


def deg2rad(degrees: float) -> float:
    return degrees * pi / 180


class VectorLike:
    @property
    def length(self):
        raise NotImplementedError()

    @property
    def angle(self):
        raise NotImplementedError()

    @property
    def angle_ortho(self):
        return self.angle + pi / 2


@dataclass(frozen=True)
class Point(VectorLike):
    x: float
    y: float

    @classmethod
    def polar(cls, r: float, theta: float):
        return cls(cos(theta), sin(theta)) * r

    @property
    def length(self):
        """Distance from origin, as though a Vector."""
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    @property
    def angle(self):
        """Angle from origin, as though a Vector."""
        x = self.x
        if 0 == x:
            x = 0.00001
        ret = atan2(self.y, x)
        return ret

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

    def __sub__(self, other: object) -> Self:
        if not isinstance(other, type(self)):
            raise NotImplementedError()
        return self + other.mirror_x.mirror_y

    @property
    def tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def mirror_x(self) -> Self:
        return type(self)(-self.x, self.y)

    @property
    def mirror_y(self) -> Self:
        return type(self)(self.x, -self.y)


@dataclass(frozen=True)
class Segment(VectorLike):
    start: Point
    end: Point

    @property
    def delta(self) -> Point:
        delta = self.end - self.start
        dx = delta.x
        if 0 == dx:
            dx = 0.00001
        return Point(dx, delta.y)

    @property
    def angle(self) -> float:
        return self.delta.angle

    @property
    def length(self) -> float:
        return self.delta.length

    @property
    def reversed(self) -> Self:
        return type(self)(self.end, self.start)

    @property
    def asc_x(self) -> Self:
        if self.start.x < self.end.x:
            return self
        return self.reversed

    @property
    def asc_y(self) -> Self:
        if self.start.y < self.end.y:
            return self
        return self.reversed

    @property
    def tuple(self) -> tuple[float, float, float, float]:
        return (
            self.start.x,
            self.start.y,
            self.end.x,
            self.end.y,
        )


def rotated_size(p1: Point, p2: Point) -> float:
    dx = abs(p2.x - p1.x)
    dy = abs(p2.y - p1.y)
    return (dx + dy) * sqrt2over2


def summation_sequence(
    lengths: Sequence[float],
) -> list[float]:
    seq = []
    acc = 0
    for length in lengths:
        acc += length
        seq.append(acc)
    return seq


def symetric_mirrored_summation_sequence(
    lengths: Sequence[float],
) -> list[float]:
    seq = summation_sequence(lengths)
    return [-i for i in reversed(seq)] + seq
