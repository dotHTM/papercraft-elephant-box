from __future__ import annotations

from dataclasses import dataclass

from drawsvg import Circle
from drawsvg import Group
from drawsvg import Line
from drawsvg import Path

from elephantbox.boxes.component.Abstract import RectangularBox
from elephantbox.boxes.component.Defaults import FINGER_CUTS_KWARGS
from elephantbox.boxes.component.Defaults import TAB_CUT_KWARGS
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import Segment
from elephantbox.math.Geometry import summation_sequence
from elephantbox.math.Geometry import symetric_mirrored_summation_sequence
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Laserable import Gridable


@dataclass(frozen=True)
class FivePanelFingerBox(
    RectangularBox,
    Gridable,
    Argumentable,
):
    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + []

    @property
    def vertical_rails(self) -> list[float]:
        seq = symetric_mirrored_summation_sequence(
            [self.width / 2, self.stock_thickness]
        )
        offset = (-6 * self.dpi) - min(seq)
        return [i + offset for i in seq]

    @property
    def horizontal_rails(self) -> list[float]:
        seq = symetric_mirrored_summation_sequence(
            [self.height / 2, self.stock_thickness, self.depth]
        )
        offset = 0
        return [i + offset for i in seq]

    @property
    def sides_origin(self) -> Point:
        return Point(
            self.vertical_rails[3] + self.stock_thickness + 10,
            self.horizontal_rails[0],
        )

    def guides(self) -> Group:
        grp = super().guides()
        sides = Group()

        # sides.append(
        #     Rectangle(
        #         **DEBUG_OBJ_KWARGS,
        #     )
        # )

        grp.append(sides)

        return grp

    def cut_outline(self) -> Group:
        grp = Group()
        dots = Group()
        d = self.dasher

        main_cut_path = Path(**FINGER_CUTS_KWARGS)
        main_cut_path.M(
            self.vertical_rails[3],
            self.horizontal_rails[0],
        )

        r = len(self.horizontal_rails)

        seq = []
        for j in range(r - 1):
            k = (j + 1) % r
            seq.append((3, j, k))
        for j in reversed(range(r - 1)):
            k = (j + 1) % r
            seq.append((0, k, j))
        for i, j, k in seq:
            start = Point(self.vertical_rails[i], self.horizontal_rails[j])
            end = Point(self.vertical_rails[i], self.horizontal_rails[k])

            d.drive_zigzag(main_cut_path, Segment(start, end))

            dots.append(
                Circle(
                    *start.tuple,
                    5,
                    fill="blue",
                    opacity="50%",
                )
            )
            dots.append(
                Circle(
                    *end.tuple,
                    5,
                    fill="#0000",
                    stroke="red",
                    stroke_width=5,
                    opacity="50%",
                )
            )

        main_cut_path.Z()
        grp.append(main_cut_path)

        sides_cut_path = Path(**FINGER_CUTS_KWARGS)

        sides_cut_path.M(*self.sides_origin.tuple)

        side_points = [
            Point(0, 0),
            Point(0, self.depth),
            Point(0, 2 * self.depth),
            Point(self.height, 2 * self.depth),
            Point(self.height, self.depth),
            Point(self.height, 0),
            Point(0, 0),
        ]
        last_point = None
        for destination in side_points:
            if last_point is not None:
                start = self.sides_origin + last_point
                end = self.sides_origin + destination

                d.drive_zigzag(
                    sides_cut_path,
                    Segment(start, end),
                )

                dots.append(
                    Circle(
                        *start.tuple,
                        5,
                        fill="blue",
                        opacity="50%",
                    )
                )
                dots.append(
                    Circle(
                        *end.tuple,
                        5,
                        fill="#0000",
                        stroke="red",
                        stroke_width=5,
                        opacity="50%",
                    )
                )
            last_point = destination

        # sides_cut_path.Z()
        grp.append(sides_cut_path)

        if self.debug:
            grp.append(dots)

        return grp

    def inner_cuts(self) -> Group:
        grp = Group()
        grp.append(
            self.dasher.zigzag(
                Segment(
                    Point(
                        self.vertical_rails[0],
                        self.horizontal_rails[1],
                    ),
                    Point(
                        self.vertical_rails[3],
                        self.horizontal_rails[1],
                    ),
                ),
                **TAB_CUT_KWARGS,
            )
        )

        grp.append(
            self.dasher.zigzag(
                Segment(
                    Point(self.vertical_rails[3], self.horizontal_rails[4]),
                    Point(self.vertical_rails[0], self.horizontal_rails[4]),
                ),
                **TAB_CUT_KWARGS,
            )
        )

        grp.append(
            Line(
                *(self.sides_origin + Point(0, self.depth)).tuple,
                *(self.sides_origin + Point(self.height, self.depth)).tuple,
                **TAB_CUT_KWARGS,
            )
        )

        return grp


@dataclass(frozen=True)
class CompactFivePanelFingerBox(
    FivePanelFingerBox,
):
    @property
    def main_origin(self):
        return Point(min(self.vertical_rails), min(self.horizontal_rails))

    @property
    def vertical_rails(self) -> list[float]:
        seq = summation_sequence(
            [
                0,
                self.stock_thickness,
                self.width,
                self.stock_thickness,
                self.height,
                self.stock_thickness,
            ]
        )
        offset = (-6 * self.dpi) - min(seq)
        return [i + offset for i in seq]

    @property
    def horizontal_rails(self) -> list[float]:
        seq = summation_sequence(
            [
                self.stock_thickness,
                self.depth,
                self.depth,
                self.stock_thickness,
                self.height,
            ]
        )

        offset = -max(seq) / 2
        return [i + offset for i in seq]

    def inner_cuts(self) -> Group:
        grp = Group()
        grp.append(
            self.dasher.zigzag(
                Segment(
                    Point(
                        self.vertical_rails[0],
                        self.horizontal_rails[2],
                    ),
                    Point(
                        self.vertical_rails[3],
                        self.horizontal_rails[2],
                    ),
                ),
                **TAB_CUT_KWARGS,
            )
        )

        little_path = Path(**TAB_CUT_KWARGS)
        little_path.M(self.vertical_rails[3], self.horizontal_rails[0])
        self.dasher.drive_zigzag(
            little_path,
            Segment(
                Point(self.vertical_rails[3], self.horizontal_rails[0]),
                Point(self.vertical_rails[3], self.horizontal_rails[1]),
            ),
        )
        self.dasher.drive_zigzag(
            little_path,
            Segment(
                Point(self.vertical_rails[3], self.horizontal_rails[1]),
                Point(self.vertical_rails[3], self.horizontal_rails[2]),
            ),
        )
        grp.append(little_path)

        grp.append(
            Line(
                *(self.main_origin + Point(0, self.depth)).tuple,
                *(
                    self.main_origin
                    + Point(
                        self.width + self.height + 2 * self.stock_thickness,
                        self.depth,
                    )
                ).tuple,
                **TAB_CUT_KWARGS,
            )
        )

        return grp

    def cut_outline(self) -> Group:
        grp = Group()
        dots = Group()
        d = self.dasher

        main_cut_path = Path(**FINGER_CUTS_KWARGS)

        seq = [
            (3, 2, False),
            (3, 3, False),
            (3, 4, False),
            #
            (0, 4, False),
            (0, 3, False),
            (0, 2, False),
            #
            (0, 1, False),
            (0, 0, False),
            #
            (3, 0, True),
            #
            (4, 0, True),
            (4, 1, True),
            (4, 2, True),
            (3, 2, True),
        ]
        end = None
        for ix, iy, invert in seq:
            start = Point(self.vertical_rails[ix], self.horizontal_rails[iy])
            if end is None:
                main_cut_path.M(*start.tuple)
                dots.append(
                    Circle(
                        *start.tuple,
                        15,
                        fill="#0000",
                        stroke="green",
                        stroke_width=5,
                        opacity="50%",
                    )
                )
            else:
                d.drive_zigzag(
                    main_cut_path,
                    Segment(
                        end,
                        start,
                    ),
                    invert=invert,
                )
                if self.debug:
                    dots.append(
                        Circle(
                            *start.tuple,
                            5,
                            fill="blue",
                            opacity="50%",
                        )
                    )
                    dots.append(
                        Circle(
                            *end.tuple,
                            5,
                            fill="#0000",
                            stroke="red",
                            stroke_width=5,
                            opacity="50%",
                        )
                    )
            end = start
        if end is not None:
            dots.append(
                Circle(
                    *end.tuple,
                    15,
                    fill="#0000",
                    stroke="red",
                    stroke_width=5,
                    opacity="50%",
                )
            )
        # main_cut_path.Z()
        grp.append(main_cut_path)

        if self.debug:
            grp.append(dots)

        return grp
