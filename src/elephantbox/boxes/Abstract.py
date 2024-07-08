from dataclasses import dataclass


from elephantbox.boxes.Dash import Dasher
from elephantbox.math.Geometry import Point
from elephantbox.support.Argumentable import AKW_TYPE, Argumentable, fl_akw
from elephantbox.support.Validatable import Validatable
from elephantbox.support.Laserable import Laserable


@dataclass(frozen=True)
class Box(Validatable, Laserable, Argumentable):
    origin: Point
    corner_saver: float
    cardstock_thickness: float
    dasher: Dasher

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--corner-saver", "-c"),
            fl_akw("--cardstock-thickness", "-s"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (0 <= self.corner_saver, "Corner Saver -ge Zero")
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
