from __future__ import annotations

from dataclasses import dataclass

from drawsvg import Circle
from drawsvg import Group
from drawsvg import Path
from drawsvg import Rectangle

from elephantbox.boxes.component.Abstract import RectangularBox
from elephantbox.boxes.component.CircleLock import CicleLock
from elephantbox.cli import main_maker
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import sqrt2over2
from elephantbox.math.Geometry import symetric_mirrored_summation_sequence
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Laserable import Laserable
from elephantbox.support.Laserable import SpanableList


DEBUG_OBJ_KWARGS = {
    "fill": "grey",
    "stroke": "blue",
    "stroke_width": 10,
    "opacity": "10%",
}

TAB_CUT_KWARGS = {
    "fill": "yellow",
    "stroke": "blue",
    "stroke_width": 2,
}

SLOT_CUT_KWARGS = {
    "fill": "lime",
    "stroke": "blue",
    "stroke_width": 2,
}


@dataclass(frozen=True)
class WatchBox(
    RectangularBox,
    Laserable,
    Argumentable,
):
    lock_radius: float
    lock_tab_angle: float
    lock_gap_cut: float
    lock_fold_height: float | None

    # lock_offset_x: float
    # lock_offset_y: float

    @classmethod
    def dimension_arguments(cls) -> list[AKW_TYPE]:
        return super().dimension_arguments() + [
            fl_akw("--lock-radius"),
            fl_akw("--lock-gap-cut"),
            fl_akw("--lock-fold-height"),
        ]

    @classmethod
    def feature_arguments(cls) -> list[AKW_TYPE]:
        return super().feature_arguments() + [
            fl_akw("--lock-tab-angle"),
        ]

    @property
    def CircleLock(self):
        return CicleLock(
            radius=self.lock_radius,
            tab_angle_deg=self.lock_tab_angle,
            gap_cut=self.lock_gap_cut,
            fold_height=self.lock_fold_height,
            corner_saver=self.corner_saver,
            dasher=self.dasher,
        )

    @property
    def vertical_rails(self) -> list[float]:
        return symetric_mirrored_summation_sequence(
            [self.width / 2, self.depth]
        )

    @property
    def horizontal_rails(self) -> list[float]:
        return symetric_mirrored_summation_sequence(
            [self.height / 2, self.depth]
        )

    @property
    def flap_thick(self):
        return min(self.width, self.height)

    @property
    def semi_flap_length(self):
        return max(self.width, self.height)

    def foldList(self) -> SpanableList:
        ret: SpanableList = []

        hp = symetric_mirrored_summation_sequence(
            [
                self.width / 2 - self.corner_saver,
                2 * self.corner_saver,
                self.depth - 2 * self.corner_saver,
            ]
        )
        for h in self.horizontal_rails:
            ret.append(
                (Point(hp[2], h), Point(hp[3], h)),
            )

            if h != min(self.horizontal_rails) and h != max(
                self.horizontal_rails
            ):
                ret.extend(
                    [
                        (Point(hp[0], h), Point(hp[1], h)),
                        (Point(hp[4], h), Point(hp[5], h)),
                    ]
                )

        vp = symetric_mirrored_summation_sequence(
            [
                self.height / 2 - self.corner_saver,
                2 * self.corner_saver,
                self.depth - 2 * self.corner_saver,
            ]
        )
        for v in self.vertical_rails:
            ret.append(
                (Point(v, vp[2]), Point(v, vp[3])),
            )

            if v != min(self.vertical_rails) and v != max(self.vertical_rails):
                ret.extend(
                    [
                        (Point(v, vp[0]), Point(v, vp[1])),
                        (Point(v, vp[4]), Point(v, vp[5])),
                    ]
                )

        diagonal_inner = sqrt2over2 * self.corner_saver
        diagonal_outer = sqrt2over2 * (self.depth - self.corner_saver)

        ret.extend(
            [
                (
                    Point(
                        (self.width / 2 + diagonal_inner),
                        (self.height / 2 + diagonal_inner),
                    ),
                    Point(
                        (self.width / 2 + diagonal_outer),
                        (self.height / 2 + diagonal_outer),
                    ),
                ),
                (
                    Point(
                        -(self.width / 2 + diagonal_outer),
                        (self.height / 2 + diagonal_outer),
                    ),
                    Point(
                        -(self.width / 2 + diagonal_inner),
                        (self.height / 2 + diagonal_inner),
                    ),
                ),
                (
                    Point(
                        (self.width / 2 + diagonal_inner),
                        -(self.height / 2 + diagonal_inner),
                    ),
                    Point(
                        (self.width / 2 + diagonal_outer),
                        -(self.height / 2 + diagonal_outer),
                    ),
                ),
                (
                    Point(
                        -(self.width / 2 + diagonal_outer),
                        -(self.height / 2 + diagonal_outer),
                    ),
                    Point(
                        -(self.width / 2 + diagonal_inner),
                        -(self.height / 2 + diagonal_inner),
                    ),
                ),
            ]
        )

        return ret

    def guide(self) -> Group:
        grp = Group()

        lhh = None
        for h in self.horizontal_rails:
            lhv = None
            for v in self.vertical_rails:
                grp.append(Circle(v, h, self.corner_saver, **DEBUG_OBJ_KWARGS))
                if lhv is not None and lhh is not None:
                    grp.append(
                        Rectangle(
                            *(lhv, lhh),
                            *(abs(v - lhv), abs(h - lhh)),
                            **DEBUG_OBJ_KWARGS,
                        )
                    )
                lhv = v
            lhh = h

        flap_thick = self.flap_thick
        semi_flap_length = self.semi_flap_length

        grp.append(
            Rectangle(
                *(-self.width / 2, min(self.horizontal_rails) - flap_thick),
                *(flap_thick, flap_thick),
                **DEBUG_OBJ_KWARGS,
            )
        )
        grp.append(
            Rectangle(
                *(-self.width / 2, max(self.horizontal_rails)),
                *(flap_thick, flap_thick),
                **DEBUG_OBJ_KWARGS,
            )
        )

        grp.append(
            Rectangle(
                *(
                    -self.width / 2 - self.depth - flap_thick,
                    -self.height / 2,
                ),
                *(flap_thick, semi_flap_length),
                **DEBUG_OBJ_KWARGS,
            )
        )
        grp.append(
            Rectangle(
                *(
                    self.width / 2 + self.depth,
                    -self.height / 2,
                ),
                *(flap_thick, semi_flap_length),
                **DEBUG_OBJ_KWARGS,
            )
        )

        return grp

    def cut_outline(self) -> Group:
        grp = Group()

        flap_thick = self.flap_thick

        cut_path = Path(
            fill="#aaaaff",
            stroke="black",
            stroke_width=5,
        )
        cut_path.M(self.vertical_rails[0], self.horizontal_rails[1]).a(
            *(self.depth, self.depth),
            *(0, 0, 1),
            *(self.depth, -self.depth),
        ).v(-flap_thick / 2).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(flap_thick, 0),
        ).v(
            flap_thick / 2
        ).a(
            *(self.depth, self.depth),
            *(0, 0, 1),
            *(self.depth, self.depth),
        ).h(
            flap_thick / 2
        ).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(flap_thick / 2, flap_thick / 2),
        ).v(
            self.height - flap_thick
        ).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(-flap_thick / 2, flap_thick / 2),
        ).h(
            -flap_thick / 2
        ).a(
            *(self.depth, self.depth),
            *(0, 0, 1),
            *(-self.depth, self.depth),
        ).v(
            flap_thick / 2
        ).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(-flap_thick, 0),
        ).v(
            -flap_thick / 2
        ).a(
            *(self.depth, self.depth),
            *(0, 0, 1),
            *(-self.depth, -self.depth),
        ).h(
            -flap_thick / 2
        ).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(-flap_thick / 2, -flap_thick / 2),
        ).v(
            -self.height + flap_thick
        ).a(
            *(flap_thick / 2, flap_thick / 2),
            *(0, 0, 1),
            *(flap_thick / 2, -flap_thick / 2),
        ).h(
            flap_thick / 2
        ).Z()

        grp.append(cut_path)

        grp.append(Circle(0, 0, 10))
        return grp

    def inner_cuts(self) -> Group:
        grp = Group(
            transform=f"translate( {self.origin.x} {self.origin.y} )",
        )

        grp.extend(
            [
                self.CircleLock.draw_slot(
                    Point(
                        0, (self.height / 2 + self.depth + self.flap_thick / 2)
                    ),
                    180,
                    SLOT_CUT_KWARGS,
                ),
                self.CircleLock.draw_slot(
                    Point(
                        0, -(self.height / 2 + self.depth + self.flap_thick / 2)
                    ),
                    0,
                    SLOT_CUT_KWARGS,
                ),
                self.CircleLock.draw_tab(
                    Point(
                        self.width / 2 + self.depth + self.flap_thick / 2,
                        (self.height / 2 - self.flap_thick / 2),
                    ),
                    0,
                    TAB_CUT_KWARGS,
                ),
                self.CircleLock.draw_tab(
                    Point(
                        self.width / 2 + self.depth + self.flap_thick / 2,
                        -(self.height / 2 - self.flap_thick / 2),
                    ),
                    180,
                    TAB_CUT_KWARGS,
                ),
            ]
        )

        return grp


main = main_maker(WatchBox, origin=Point(-6, -6))
