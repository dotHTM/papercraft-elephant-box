from __future__ import annotations

from dataclasses import dataclass

from drawsvg import Group
from drawsvg import Line
from drawsvg import Path

from elephantbox.boxes.component.Abstract import RectangularBox
from elephantbox.boxes.component.Defaults import FINGER_CUTS_KWARGS
from elephantbox.boxes.component.Defaults import TAB_CUT_KWARGS
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import Segment
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
        return super().vertical_rails + [i + offset for i in seq]

    @property
    def horizontal_rails(self) -> list[float]:
        seq = symetric_mirrored_summation_sequence(
            [self.height / 2, self.stock_thickness, self.depth]
        )
        offset = 0
        return super().vertical_rails + [i + offset for i in seq]

    @property
    def sides_origin(self) -> Point:
        return Point(
            self.vertical_rails[3] + self.stock_thickness + 10,
            self.horizontal_rails[0],
        )

    def cut_outline(self) -> Group:
        grp = Group()
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
            d.drive_zigzag(
                main_cut_path,
                Segment(
                    Point(self.vertical_rails[i], self.horizontal_rails[j]),
                    Point(self.vertical_rails[i], self.horizontal_rails[k]),
                ),
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
                d.drive_zigzag(
                    sides_cut_path,
                    Segment(
                        self.sides_origin + last_point,
                        self.sides_origin + destination,
                    ),
                )
            last_point = destination

        # sides_cut_path.Z()
        grp.append(sides_cut_path)

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
