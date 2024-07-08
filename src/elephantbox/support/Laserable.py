from __future__ import annotations

from drawsvg import Group
from drawsvg import Line

from elephantbox.boxes.component.Dash import Dasher
from elephantbox.math.Geometry import Point


SpanableList = list[tuple[Point, Point]]


class FoldListable:
    dasher: Dasher

    def foldList(self) -> SpanableList:
        return []

    def folds(self) -> Group:
        grp = Group()
        for fl in self.foldList():
            grp.append(
                self.dasher.span(
                    *fl,
                    stroke="red",
                    stroke_width=2,
                )
            )
        return grp


class InnerCutListable:
    def innerCutList(self) -> SpanableList:
        return []

    def inner_cuts(self) -> Group:
        grp = Group()
        for p1, p2 in self.innerCutList():
            foldLine = Line(
                *(p1.x, p1.y, p2.x, p2.y),
                stroke="blue",
                stroke_width=2,
            )
            grp.append(foldLine)

        return grp


class Laserable(FoldListable, InnerCutListable):
    def guides(self) -> Group:
        return Group()

    def cut_outline(self) -> Group:
        return Group()

    def draw(self, guides: bool = False) -> Group:
        grp = Group()
        if guides:
            grp.append(self.guides())
        grp.append(self.cut_outline())
        grp.append(self.folds())
        grp.append(self.inner_cuts())
        return grp
