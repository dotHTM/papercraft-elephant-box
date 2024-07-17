from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from drawsvg import Circle
from drawsvg import Group
from drawsvg import Line
from drawsvg import Path

from elephantbox.boxes.component.Defaults import DEBUG_OBJ_KWARGS
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import Segment
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Validatable import Validatable


@dataclass(frozen=True)
class Dasher(Validatable, Argumentable):
    model_dash_length: float
    model_dash_period: float
    stock_thickness: float

    @classmethod
    @property
    def meta_name(cls) -> str:
        return "Dash"

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--dash-length", dest="model_dash_length"),
            fl_akw("--dash-period", dest="model_dash_period"),
            fl_akw("--stock-thickness"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (
                0 < self.model_dash_length,
                "model_dash_length is greater than Zero",
            ),
            (
                0 < self.model_dash_period,
                "model_dash_period is greater than Zero",
            ),
        ]

    def span_sequence(
        self,
        segment: Segment,
    ) -> list[Segment]:
        dash_line = []

        period_count = ceil(
            (segment.length - self.model_dash_length + 0.001)
            / self.model_dash_period
        )
        model_length = (
            self.model_dash_length + period_count * self.model_dash_period
        )
        scale_factor = segment.length / model_length

        actual_dash_length_vector = Point.polar(
            self.model_dash_length * scale_factor, segment.angle
        )
        actual_period_vector = Point.polar(
            self.model_dash_period * scale_factor, segment.angle
        )

        for n in range(period_count + 1):
            start = segment.start + (actual_period_vector * n)
            end = start + actual_dash_length_vector

            dash_line.append(Segment(start, end))

        # print(segment.angle)
        # print(actual_dash_length_vector)
        # print(actual_period_vector)

        return dash_line

    def span(
        self,
        origin: Point,
        destination: Point,
        **kwargs,
    ) -> Group:
        self.validate()
        dashes = Group()

        for segment in self.span_sequence(
            Segment(
                origin,
                destination,
            )
        ):
            dashes.append(
                Line(
                    *segment.tuple,
                    **kwargs,
                )
            )

        if self.debug:
            dashes.append(Circle(*origin.tuple, 5, **DEBUG_OBJ_KWARGS))
            dashes.append(Circle(*destination.tuple, 5, **DEBUG_OBJ_KWARGS))

        return dashes

    def drive_zigzag(
        self,
        path: Path,
        segment: Segment,
        invert: bool = False,
    ) -> Path:
        self.validate()
        ortho_delta = Point.polar(
            self.stock_thickness, segment.delta.angle_ortho
        )
        if invert:
            ortho_delta *= -1
        path.L(*segment.start.tuple)
        last_endpoint = None
        for dash in self.span_sequence(segment):
            if last_endpoint is not None:
                in_point = last_endpoint + ortho_delta
                out_point = dash.start + ortho_delta
                path.L(*in_point.tuple)
                path.L(*out_point.tuple)
                path.L(*dash.start.tuple)
            path.L(*dash.end.tuple)
            last_endpoint = dash.end
        return path

    def zigzag(
        self,
        segment: Segment,
        invert: bool = False,
        **kwargs,
    ) -> Group:
        dashes = Group()

        cut_path = Path(**kwargs)
        cut_path.M(*segment.start.tuple)
        self.drive_zigzag(
            path=cut_path,
            segment=segment,
            invert=invert,
        )
        if self.debug:
            dashes.append(Circle(*segment.start.tuple, 5, **DEBUG_OBJ_KWARGS))
            dashes.append(Circle(*segment.end.tuple, 5, **DEBUG_OBJ_KWARGS))

        dashes.append(cut_path)
        return dashes
