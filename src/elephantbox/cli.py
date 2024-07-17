from __future__ import annotations

from elephantbox.boxes.assembly.Finger import CompactFivePanelFingerBox
from elephantbox.boxes.assembly.Finger import FivePanelFingerBox
from elephantbox.boxes.tuck.Elephant import ElephantBox
from elephantbox.boxes.tuck.Watch import WatchBox
from elephantbox.math.Geometry import Point
from elephantbox.support.cli import main_maker


ElephantBoxMain = main_maker(ElephantBox, origin=Point(0, -6))
WatchBoxMain = main_maker(WatchBox, origin=Point(-6, -6))
FivePanelFingerBoxMain = main_maker(FivePanelFingerBox, origin=Point(-6, -6))
CompactFivePanelFingerBoxMain = main_maker(
    CompactFivePanelFingerBox, origin=Point(-6, -6)
)
