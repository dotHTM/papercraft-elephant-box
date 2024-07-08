from __future__ import annotations

from dataclasses import dataclass
from math import atan
from math import ceil
from math import cos
from math import sin
from math import sqrt

from drawsvg import Group
from drawsvg import Line

from elephantbox.math.Geometry import Point
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Validatable import Validatable


@dataclass(frozen=True)
class Dasher(Validatable, Argumentable):
    max_dash_length: float
    dash_period: float

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--max-dash-length"),
            fl_akw("--dash-period"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (0 < self.max_dash_length, "max_dash_length is greater than Zero"),
            (0 < self.dash_period, "dash_period is greater than Zero"),
        ]

    def span(
        self,
        origin: Point,
        destination: Point,
        **kwargs,
    ) -> Group:
        self.validate()

        dx = destination.x - origin.x
        dy = destination.y - origin.y

        if dx == 0:
            dx = 0.00001
        direction = atan(dy / dx)

        actual_length = sqrt(pow(dx, 2) + pow(dy, 2))

        period_count = ceil(
            (actual_length - self.max_dash_length) / self.dash_period
        )
        max_length = self.max_dash_length + period_count * self.dash_period
        scale_factor = actual_length / max_length
        actual_dash_length = self.max_dash_length * scale_factor
        actual_period = self.dash_period * scale_factor

        adl_x = actual_dash_length * cos(direction)
        adl_y = actual_dash_length * sin(direction)

        ap_x = actual_period * cos(direction)
        ap_y = actual_period * sin(direction)

        dashes = Group()

        for n in range(period_count + 1):
            this_dash_start_x = origin.x + n * ap_x
            this_dash_start_y = origin.y + n * ap_y
            this_dash_end_x = this_dash_start_x + adl_x
            this_dash_end_y = this_dash_start_y + adl_y

            dashes.append(
                Line(
                    this_dash_start_x,
                    this_dash_start_y,
                    this_dash_end_x,
                    this_dash_end_y,
                    **kwargs,
                )
            )

        return dashes
