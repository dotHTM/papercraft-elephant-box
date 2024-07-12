from __future__ import annotations

from elephantbox.boxes.tuck.Elephant import ElephantBox
from elephantbox.boxes.tuck.Watch import WatchBox
from elephantbox.math.Geometry import Point
from elephantbox.support.cli import main_maker


ElephantBox = main_maker(ElephantBox, origin=Point(0, -6))
WatchBox = main_maker(WatchBox, origin=Point(-6, -6))
