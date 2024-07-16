from __future__ import annotations

from drawsvg import Group
from drawsvg import Line
from drawsvg import Rectangle

from elephantbox.boxes.component.Dash import Dasher
from elephantbox.boxes.component.Defaults import DEBUG_OBJ_KWARGS
from elephantbox.boxes.component.Defaults import FOLD_PERFERATION_KWARGS
from elephantbox.boxes.component.Defaults import SLOT_CUT_KWARGS
from elephantbox.math.Geometry import Point


SpanableList = list[tuple[Point, Point]]


class FoldListable:
    dasher: Dasher

    def foldList(self) -> SpanableList:
        return []

    def folds(self) -> Group:
        grp = Group()
        for fl in self.foldList():
            grp.append(self.dasher.span(*fl, **FOLD_PERFERATION_KWARGS))
        return grp


class InnerCutListable:
    def innerCutList(self) -> SpanableList:
        return []

    def inner_cuts(self) -> Group:
        grp = Group()
        for p1, p2 in self.innerCutList():
            foldLine = Line(
                *(p1.x, p1.y, p2.x, p2.y),
                **SLOT_CUT_KWARGS,
            )
            grp.append(foldLine)

        return grp


class Laserable(FoldListable, InnerCutListable):
    laser_bed_origin = Point(0, 0)

    def guides(self) -> Group:
        return Group()

    def cut_outline(self) -> Group:
        return Group()

    def draw(self, enable_guides: bool = False) -> Group:
        grp = Group(
            transform=f"translate({self.laser_bed_origin.x} {self.laser_bed_origin.y})"
        )
        if enable_guides:
            grp.append(self.guides())
        grp.append(self.cut_outline())
        grp.append(self.folds())
        grp.append(self.inner_cuts())
        return grp


class Gridable(Laserable):
    @property
    def vertical_rails(self) -> list[float]:
        return []

    @property
    def horizontal_rails(self) -> list[float]:
        return []

    def guides(self) -> Group:
        grp = super().guides()
        grid = Group()

        lhh = None
        for h in self.horizontal_rails:
            lhv = None
            for v in self.vertical_rails:
                if lhv is not None and lhh is not None:
                    grid.append(
                        Rectangle(
                            *(lhv, lhh),
                            *(abs(v - lhv), abs(h - lhh)),
                            **DEBUG_OBJ_KWARGS,
                        )
                    )
                lhv = v
            lhh = h

        grp.append(grid)
        return grp
