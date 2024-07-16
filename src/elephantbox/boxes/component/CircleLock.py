from __future__ import annotations

from dataclasses import dataclass
from math import cos
from math import sin
from math import sqrt

from drawsvg import Circle
from drawsvg import Group
from drawsvg import Path

from elephantbox.boxes.component.Dash import Dasher
from elephantbox.math.Geometry import deg2rad
from elephantbox.math.Geometry import Point
from elephantbox.support.Validatable import Validatable


@dataclass(frozen=True)
class CicleLock(Validatable):
    radius: float
    tab_angle_deg: float
    gap_cut: float
    fold_height: float | None

    dasher: Dasher

    fold_perferation: bool = False
    corner_saver: float = 0
    show_guides: bool = False

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (0 <= self.corner_saver, "positive corner_saver"),
            (
                -self.fold_height <= self.gap_cut
                if self.fold_height is not None and self.fold_height < 0
                else True,
                "Real Fold solution when Fold Height is negative",
            ),
        ]

    @property
    def tab_angle(self):
        return deg2rad(self.tab_angle_deg)

    @property
    def unit_corner_point(self) -> Point:
        return Point(
            cos(self.tab_angle),
            sin(self.tab_angle),
        )

    @property
    def left_slot_corner_point(self) -> Point:
        return self.unit_corner_point * self.radius

    @property
    def inner_gap_corner_point(self) -> Point:
        return self.unit_corner_point * (self.radius - self.gap_cut)

    @property
    def outer_gap_corner_point(self) -> Point:
        return self.unit_corner_point * (self.radius + self.gap_cut)

    @property
    def inner_fold_radius(self) -> float:
        return self.radius - self.gap_cut - self.corner_saver

    @property
    def divider(self) -> Point:
        return (
            Point(cos(self.tab_angle), sin(self.tab_angle))
            * self.inner_fold_radius
        )

    @property
    def fold_left(self) -> Point:
        if self.fold_height is None:
            raise Exception("No fold_height")
        position_y = self.left_slot_corner_point.y - self.fold_height
        position_x = 0

        if position_y > self.divider.y:
            position_x = self.left_slot_corner_point.x - sqrt(
                pow(self.gap_cut + self.corner_saver, 2)
                - pow(self.fold_height, 2)
            )
        else:
            position_x = sqrt(
                pow(self.inner_fold_radius, 2) - pow(position_y, 2)
            )

        return Point(position_x, position_y)

    def draw_tab(
        self, origin: Point, angle: float, cut_obj_kwargs: dict = {}
    ) -> Group:
        grp = Group(
            transform=f"translate( {origin.x} {origin.y} ) rotate( {angle} )",
        )

        A = self.inner_gap_corner_point
        B = self.inner_gap_corner_point.mirror_x
        C = self.outer_gap_corner_point.mirror_x
        D = self.outer_gap_corner_point

        cut_path = Path(**cut_obj_kwargs)
        cut_path.M(A.x, A.y).A(
            *(self.radius - self.gap_cut, self.radius - self.gap_cut),
            *(0, 0 < self.tab_angle, 0),
            *B.tuple,
        ).A(
            *(self.gap_cut, self.gap_cut),
            *(0, 0, 1),
            *C.tuple,
        ).A(
            *(self.radius + self.gap_cut, self.radius + self.gap_cut),
            *(0, 0 < self.tab_angle, 1),
            *D.tuple,
        ).A(
            *(self.gap_cut, self.gap_cut),
            *(0, 0, 1),
            *A.tuple,
        )

        grp.append(cut_path)

        if self.fold_perferation:
            fold_line = Group(stroke="red", stroke_width=3)
            if self.fold_height is not None:
                fold_line.append(
                    self.dasher.span(self.fold_left.mirror_x, self.fold_left)
                )
            grp.append(fold_line)

        if self.show_guides:
            grp.append(
                Circle(
                    *self.divider.tuple,
                    10,
                )
            )
            grp.append(
                Circle(
                    *self.fold_left.tuple,
                    10,
                )
            )
            grp.append(
                Circle(
                    *self.fold_left.mirror_x.tuple,
                    10,
                )
            )
            grp.append(
                Circle(
                    *self.left_slot_corner_point.tuple,
                    self.gap_cut + self.corner_saver,
                    stroke="black",
                    stroke_width=1,
                    opacity="5%",
                )
            )
            grp.append(
                Circle(
                    *(0, 0),
                    self.radius - self.gap_cut - self.corner_saver,
                    stroke="black",
                    stroke_width=1,
                    opacity="5%",
                )
            )

        if self.show_guides:
            for p in A, B, C, D:
                c = Circle(*p.tuple, 10)
                grp.append(c)

        return grp

    def draw_slot(
        self, origin: Point, angle: float, cut_obj_kwargs: dict = {}
    ) -> Group:
        grp = Group(
            transform=f"translate( {origin.x} {origin.y} ) rotate( {angle} )",
        )
        cut_path = Path(**cut_obj_kwargs)

        left = self.left_slot_corner_point
        right = self.left_slot_corner_point.mirror_x

        cut_path.M(left.x, left.y).A(
            *(self.radius, self.radius),
            *(0, not 0 < self.tab_angle, 1),
            *(right.x, right.y),
        ).L(left.x, left.y).Z()

        grp.append(cut_path)
        if self.show_guides:
            grp.append(Circle(0, 0, 10))
            grp.append(Circle(left.x, left.y, 10))
            grp.append(Circle(right.x, right.y, 10))

        return grp
