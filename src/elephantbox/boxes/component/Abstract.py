from __future__ import annotations

from dataclasses import dataclass

from elephantbox.boxes.component.Dash import Dasher
from elephantbox.math.Geometry import Point
from elephantbox.support.Argumentable import akw
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Laserable import Laserable
from elephantbox.support.Validatable import Validatable


@dataclass(frozen=True)
class Box(Validatable, Laserable, Argumentable):
    origin: Point
    stock_thickness: float
    dasher: Dasher

    guide: bool

    @classmethod
    @property
    def meta_name(cls) -> str:
        return "Box"

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--stock-thickness", "-s"),
        ]

    @classmethod
    def feature_arguments(cls) -> list[AKW_TYPE]:
        return super().feature_arguments() + [
            akw("--guide", action="store_true"),
        ]


@dataclass(frozen=True)
class RectangularBox(Box):
    width: float  # x
    height: float  # y
    depth: float  # z

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--width", "-x"),
            fl_akw("--height", "-y"),
            fl_akw("--depth", "-z"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (0 < self.width, "Width -gt Zero"),
            (0 < self.height, "Height -gt Zero"),
            (0 < self.depth, "Depth -gt Zero"),
        ]


@dataclass(frozen=True)
class RectangularTuckBox(RectangularBox):
    corner_saver: float

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--corner-saver", "-c"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (0 <= self.corner_saver, "Corner Saver -ge Zero")
        ]
