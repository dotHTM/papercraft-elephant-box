from __future__ import annotations

from dataclasses import dataclass

from drawsvg import Group
from drawsvg import Path

from elephantbox.boxes.component.Abstract import RectangularBox
from elephantbox.boxes.component.Defaults import BODY_CUT_KWARGS
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import rotated_size
from elephantbox.math.Geometry import sqrt2over2
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Laserable import Laserable
from elephantbox.support.Laserable import SpanableList


@dataclass(frozen=True)
class ElephantBox(
    RectangularBox,
    Laserable,
    Argumentable,
):
    ear_flap: float
    back_support: float
    side_support: float
    nose_width: float

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--ear-flap"),
            fl_akw("--back-support"),
            fl_akw("--side-support"),
            fl_akw("--nose-width"),
        ]

    def assertions(self) -> list[tuple[bool, str]]:
        return super().assertions() + [
            (
                0 < self.ear_flap <= self.depth,
                "Non Negative Ear Flap -lt depth",
            ),
            (
                0 <= self.back_support <= self.height,
                "Pos Back Support -lt height",
            ),
            (
                0 <= self.side_support <= self.width,
                "Pos Side Support -lt width",
            ),
            (
                0 <= self.nose_width,
                "Positive nose_width",
            ),
            (
                0 <= self.nasial_labia,
                "Positive Nasial Labia",
            ),
        ]

    @property
    def body_vertical_rails(self) -> list[float]:
        return [
            self.back_support + 0,
            self.back_support + self.corner_saver,
            self.back_support + self.depth - self.corner_saver,
            self.back_support + self.depth,
            self.back_support + self.depth + self.corner_saver,
            self.back_support + self.depth + self.width - self.corner_saver,
            self.back_support + self.depth + self.width,
            self.back_support + self.depth + self.width + self.corner_saver,
            self.back_support + self.depth * 2 + self.width - self.corner_saver,
            self.back_support + self.depth * 2 + self.width,
        ]

    @property
    def body_horizontal_rails(self) -> list[float]:
        return [
            -(self.height / 2 + self.depth),
            -(self.height / 2 + self.depth - self.corner_saver),
            -(self.height / 2 + self.corner_saver),
            -(self.height / 2),
            -(self.height / 2 - self.corner_saver),
            (self.height / 2 - self.corner_saver),
            (self.height / 2),
            (self.height / 2 + self.corner_saver),
            (self.height / 2 + self.depth - self.corner_saver),
            (self.height / 2 + self.depth),
        ]

    @property
    def ear_width(self) -> float:
        return self.width - self.stock_thickness

    @property
    def head_width(self) -> float:
        return self.width + self.stock_thickness

    @property
    def head_height(self) -> float:
        return self.height - self.stock_thickness

    @property
    def nasial_labia(self) -> float:
        return (self.head_height - 2 * self.ear_flap - self.nose_width) / 2

    @property
    def diagonal_deck_thickness(self) -> float:
        return self.depth * sqrt2over2

    @property
    def diagonal_corner_saver(self) -> float:
        return self.corner_saver * sqrt2over2

    @property
    def neck_base(self) -> float:
        return self.body_vertical_rails[9]

    @property
    def ear_start(self) -> float:
        return self.neck_base + self.stock_thickness

    @property
    def nose_start(self) -> float:
        return self.neck_base + self.head_width + self.ear_flap

    @property
    def rear_ear_radius(self) -> float:
        return self.ear_flap / 2

    @property
    def nose_tip_end(self) -> float:
        ret = self.neck_base + self.head_width + self.ear_flap
        if self.nose_width:
            ret += self.ear_flap + self.nose_width / 2
        return ret

    @property
    def point_diagonal_top_left(self) -> Point:
        return Point(
            (self.body_vertical_rails[3] - self.diagonal_deck_thickness),
            (self.body_horizontal_rails[3] - self.diagonal_deck_thickness),
        )

    @property
    def point_diagonal_bottom_right_nose(self) -> Point:
        return Point(
            self.nose_tip_end + (self.nose_width / 2) * (sqrt2over2 - 1),
            self.nose_width * sqrt2over2 / 2,
        )

    @property
    def point_diagonal_bottom_right_face(self) -> Point:
        return Point(
            self.ear_start + self.ear_width + self.ear_flap * (sqrt2over2),
            self.head_height / 2 - self.ear_flap * (1 - sqrt2over2),
        )

    @property
    def point_diagonal_bottom_right_ear(self) -> Point:
        return Point(
            self.ear_start + self.ear_width - self.ear_flap * (1 - sqrt2over2),
            self.head_height / 2 + self.ear_flap * (sqrt2over2),
        )

    @property
    def rotated_size(self) -> float:
        return max(
            [
                rotated_size(
                    self.point_diagonal_top_left,
                    self.point_diagonal_bottom_right_nose,
                ),
                rotated_size(
                    self.point_diagonal_top_left,
                    self.point_diagonal_bottom_right_face,
                ),
                rotated_size(
                    self.point_diagonal_top_left,
                    self.point_diagonal_bottom_right_ear,
                ),
            ]
        )

    def cut_outline(self) -> Group:
        grp = Group()

        cutPath = Path(**BODY_CUT_KWARGS)

        # # Body
        cutPath.M(self.body_vertical_rails[9], self.body_horizontal_rails[3]).A(
            *(self.depth, self.depth),
            *(0, 0, 0),
            *(self.body_vertical_rails[6], self.body_horizontal_rails[0]),
        )

        if 0 < self.side_support:
            cutPath.v(-self.side_support / 2).a(
                *(self.side_support / 2, self.side_support / 2),
                *(0, 0, 0),
                *(-self.side_support / 2, -self.side_support / 2),
            ).H(self.body_vertical_rails[3] + self.side_support / 2).a(
                *(self.side_support / 2, self.side_support / 2),
                *(0, 0, 0),
                *(-self.side_support / 2, self.side_support / 2),
            ).v(
                self.side_support / 2
            )
        else:
            cutPath.H(self.body_vertical_rails[3])

        cutPath.A(
            *(self.depth, self.depth),
            *(0, 0, 0),
            *(self.body_vertical_rails[0], self.body_horizontal_rails[3]),
        )

        if 0 < self.back_support:
            cutPath.h(-self.back_support / 2).a(
                *(self.back_support / 2, self.back_support / 2),
                *(0, 0, 0),
                *(-self.back_support / 2, self.back_support / 2),
            ).V(self.body_horizontal_rails[6] - self.back_support / 2).a(
                *(self.back_support / 2, self.back_support / 2),
                *(0, 0, 0),
                *(self.back_support / 2, self.back_support / 2),
            ).h(
                self.back_support / 2
            )
        else:
            cutPath.V(self.body_horizontal_rails[6])

        cutPath.A(
            *(self.depth, self.depth),
            *(0, 0, 0),
            *(self.body_vertical_rails[3], self.body_horizontal_rails[9]),
        )

        if 0 < self.side_support:
            cutPath.v(self.side_support / 2).a(
                *(self.side_support / 2, self.side_support / 2),
                *(0, 0, 0),
                *(self.side_support / 2, self.side_support / 2),
            ).H(self.body_vertical_rails[6] - self.side_support / 2).a(
                *(self.side_support / 2, self.side_support / 2),
                *(0, 0, 0),
                *(self.side_support / 2, -self.side_support / 2),
            ).v(
                -self.side_support / 2
            )

        else:
            cutPath.H(self.body_vertical_rails[6])

        cutPath.A(
            *(self.depth, self.depth),
            *(0, 0, 0),
            *(self.body_vertical_rails[9], self.body_horizontal_rails[6]),
        )

        # head

        cutPath.L(self.neck_base, self.head_height / 2)

        if 0 == self.ear_flap:
            cutPath.h(self.head_width)
        else:
            cutPath.L(
                self.ear_start,
                self.head_height / 2,
            ).v(self.rear_ear_radius).a(
                *(self.rear_ear_radius, self.rear_ear_radius),
                *(0, 0, 0),
                *(self.rear_ear_radius, self.rear_ear_radius),
            ).h(
                self.ear_width - self.ear_flap * 3 / 2
            ).a(
                *(self.ear_flap, self.ear_flap),
                *(0, 0, 0),
                *(self.ear_flap, -self.ear_flap),
            ).h(
                self.stock_thickness
            )

        cutPath.a(
            *(self.ear_flap, self.ear_flap),
            *(0, 0, 0),
            *(self.ear_flap, -self.ear_flap),
        ).v(-self.nasial_labia)

        if 0 == self.nose_width:
            cutPath.v(-self.nose_width)
        else:
            cutPath.h(self.ear_flap).a(
                *(self.nose_width / 2, self.nose_width / 2),
                *(0, 0, 0),
                *(0, -self.nose_width),
            ).h(-self.ear_flap)

        cutPath.v(-self.nasial_labia).a(
            *(self.ear_flap, self.ear_flap),
            *(0, 0, 0),
            *(-self.ear_flap, -self.ear_flap),
        )

        if 0 == self.ear_flap:
            cutPath.h(-self.head_width)
        else:
            cutPath.h(-self.stock_thickness).a(
                *(self.ear_flap, self.ear_flap),
                *(0, 0, 0),
                *(-self.ear_flap, -self.ear_flap),
            ).h(-(self.ear_width - self.ear_flap * 3 / 2)).a(
                *(self.rear_ear_radius, self.rear_ear_radius),
                *(0, 0, 0),
                *(-self.rear_ear_radius, self.rear_ear_radius),
            ).L(
                self.ear_start,
                -self.head_height / 2,
            )

        cutPath.L(self.neck_base, -self.head_height / 2)

        # close off
        cutPath.Z()

        grp.append(cutPath)

        return grp

    def foldList(self) -> SpanableList:
        foldList = [
            (
                Point(
                    self.body_vertical_rails[3]
                    - self.diagonal_deck_thickness
                    + self.diagonal_corner_saver,
                    self.body_horizontal_rails[3]
                    - self.diagonal_deck_thickness
                    + self.diagonal_corner_saver,
                ),
                Point(
                    self.body_vertical_rails[3] - self.diagonal_corner_saver,
                    self.body_horizontal_rails[3] - self.diagonal_corner_saver,
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[3]
                    - self.diagonal_deck_thickness
                    + self.diagonal_corner_saver,
                    self.body_horizontal_rails[6]
                    + self.diagonal_deck_thickness
                    - self.diagonal_corner_saver,
                ),
                Point(
                    self.body_vertical_rails[3] - self.diagonal_corner_saver,
                    self.body_horizontal_rails[6] + self.diagonal_corner_saver,
                ),
            ),
            # # # # # # #
            (
                Point(
                    self.body_vertical_rails[6] + self.diagonal_corner_saver,
                    self.body_horizontal_rails[3] - self.diagonal_corner_saver,
                ),
                Point(
                    self.body_vertical_rails[6]
                    + self.diagonal_deck_thickness
                    - self.diagonal_corner_saver,
                    self.body_horizontal_rails[3]
                    - self.diagonal_deck_thickness
                    + self.diagonal_corner_saver,
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[6] + self.diagonal_corner_saver,
                    self.body_horizontal_rails[6] + self.diagonal_corner_saver,
                ),
                Point(
                    self.body_vertical_rails[6]
                    + self.diagonal_deck_thickness
                    - self.diagonal_corner_saver,
                    self.body_horizontal_rails[6]
                    + self.diagonal_deck_thickness
                    - self.diagonal_corner_saver,
                ),
            ),
            # # # #
            (
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[1]
                ),
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[2]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[4]
                ),
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[5]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[7]
                ),
                Point(
                    self.body_vertical_rails[3], self.body_horizontal_rails[8]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[1]
                ),
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[2]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[4]
                ),
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[5]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[7]
                ),
                Point(
                    self.body_vertical_rails[6], self.body_horizontal_rails[8]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[1], self.body_horizontal_rails[3]
                ),
                Point(
                    self.body_vertical_rails[2], self.body_horizontal_rails[3]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[4], self.body_horizontal_rails[3]
                ),
                Point(
                    self.body_vertical_rails[5], self.body_horizontal_rails[3]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[7], self.body_horizontal_rails[3]
                ),
                Point(
                    self.body_vertical_rails[8], self.body_horizontal_rails[3]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[1], self.body_horizontal_rails[6]
                ),
                Point(
                    self.body_vertical_rails[2], self.body_horizontal_rails[6]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[4], self.body_horizontal_rails[6]
                ),
                Point(
                    self.body_vertical_rails[5], self.body_horizontal_rails[6]
                ),
            ),
            (
                Point(
                    self.body_vertical_rails[7], self.body_horizontal_rails[6]
                ),
                Point(
                    self.body_vertical_rails[8], self.body_horizontal_rails[6]
                ),
            ),
            #
            (
                Point(self.neck_base, self.body_horizontal_rails[4]),
                Point(self.neck_base, self.body_horizontal_rails[5]),
            ),
            (
                Point(
                    self.neck_base + self.stock_thickness + self.corner_saver,
                    -self.head_height / 2,
                ),
                Point(
                    self.neck_base
                    + self.stock_thickness
                    - self.corner_saver
                    + self.ear_width,
                    -self.head_height / 2,
                ),
            ),
            (
                Point(
                    self.neck_base + self.stock_thickness + self.corner_saver,
                    self.head_height / 2,
                ),
                Point(
                    self.neck_base
                    + self.stock_thickness
                    - self.corner_saver
                    + self.ear_width,
                    self.head_height / 2,
                ),
            ),
        ]

        if self.back_support:
            foldList.extend(
                [
                    (
                        Point(
                            self.body_vertical_rails[0],
                            self.body_horizontal_rails[4],
                        ),
                        Point(
                            self.body_vertical_rails[0],
                            self.body_horizontal_rails[5],
                        ),
                    ),
                ]
            )

        if self.side_support:
            foldList.extend(
                [
                    (
                        Point(
                            self.body_vertical_rails[4],
                            self.body_horizontal_rails[0],
                        ),
                        Point(
                            self.body_vertical_rails[5],
                            self.body_horizontal_rails[0],
                        ),
                    ),
                    (
                        Point(
                            self.body_vertical_rails[4],
                            self.body_horizontal_rails[9],
                        ),
                        Point(
                            self.body_vertical_rails[5],
                            self.body_horizontal_rails[9],
                        ),
                    ),
                ]
            )

            # # Ear flaps

        if 0 == self.nose_width:
            foldList.extend(
                [
                    # Face flap
                    (
                        Point(
                            self.neck_base + self.head_width,
                            (self.head_height / 2 - self.corner_saver),
                        ),
                        Point(
                            self.neck_base + self.head_width,
                            -(self.head_height / 2 - self.corner_saver),
                        ),
                    ),
                ]
            )
        else:
            foldList.extend(
                [  # nose
                    (
                        Point(
                            self.neck_base
                            + 2 * self.stock_thickness
                            + self.ear_width
                            + self.ear_flap,
                            (self.nose_width / 2 - self.corner_saver),
                        ),
                        Point(
                            self.neck_base
                            + 2 * self.stock_thickness
                            + self.ear_width
                            + self.ear_flap,
                            -(self.nose_width / 2 - self.corner_saver),
                        ),
                    ),
                    (
                        Point(
                            self.neck_base
                            + 2 * self.stock_thickness
                            + self.ear_width
                            + 2 * self.ear_flap,
                            (self.nose_width / 2 - self.corner_saver),
                        ),
                        Point(
                            self.neck_base
                            + 2 * self.stock_thickness
                            + self.ear_width
                            + 2 * self.ear_flap,
                            -(self.nose_width / 2 - self.corner_saver),
                        ),
                    ),
                ]
            )

            if 0 < self.head_height - self.nose_width - 2 * self.corner_saver:
                foldList.extend(
                    [
                        # Face flap
                        (
                            Point(
                                self.neck_base + self.head_width,
                                (self.head_height / 2 - self.corner_saver),
                            ),
                            Point(
                                self.neck_base + self.head_width,
                                (self.nose_width / 2 + self.corner_saver),
                            ),
                        ),
                        (
                            Point(
                                self.neck_base + self.head_width,
                                -(self.nose_width / 2 + self.corner_saver),
                            ),
                            Point(
                                self.neck_base + self.head_width,
                                -(self.head_height / 2 - self.corner_saver),
                            ),
                        ),
                    ]
                )
        return foldList

    def innerCutList(self) -> SpanableList:
        cutList = [
            (
                Point(
                    self.neck_base + self.head_width,
                    (self.nose_width / 2),
                ),
                Point(
                    self.neck_base + self.head_width,
                    -(self.nose_width / 2),
                ),
            )
        ]
        if 0 == self.nose_width:
            cutList = []

        return cutList
