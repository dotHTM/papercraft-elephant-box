from __future__ import annotations

from dataclasses import dataclass

from drawsvg import Group
from drawsvg import Rectangle

from elephantbox.boxes.component.Abstract import RectangularBox
from elephantbox.boxes.component.CircleLock import CicleLock
from elephantbox.cli import main_maker
from elephantbox.math.Geometry import Point
from elephantbox.math.Geometry import symetric_mirrored_summation_sequence
from elephantbox.support.Argumentable import AKW_TYPE
from elephantbox.support.Argumentable import Argumentable
from elephantbox.support.Argumentable import fl_akw
from elephantbox.support.Laserable import Laserable


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
            tab_angle=self.lock_tab_angle,
            gap_cut=self.lock_gap_cut,
            fold_height=self.lock_fold_height,
            corner_saver=self.corner_saver,
            dasher=self.dasher,
        )

    @property
    def vertical_rails(self) -> list[float]:
        return symetric_mirrored_summation_sequence(
            [
                self.width / 2,
                self.depth,
            ]
        )

    def outer_cuts(self) -> Group:
        grp = Group()

        lhv = None
        for v in self.vertical_rails:
            if lhv is not None:
                grp.append(Rectangle(v, 0, abs(v - lhv), 100))
            lhv = v
        return grp

    def inner_cuts(self) -> Group:
        grp = Group(
            transform=f"translate( {self.origin.x} {self.origin.y} )",
        )

        grp.extend(
            [
                self.CircleLock.draw_slot(Point(0, 0), 0),
                self.CircleLock.draw_tab(Point(0, 0), 0),
            ]
        )

        return grp


main = main_maker(WatchBox, origin=Point(-1800, -1800))
