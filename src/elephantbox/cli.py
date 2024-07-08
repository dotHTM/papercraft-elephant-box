from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Callable
from collections.abc import Sequence

import drawsvg

from elephantbox.boxes.Dash import Dasher
from elephantbox.boxes.Elephant import ElephantBox
from elephantbox.math.Geometry import Point


def debug_args(parser: ArgumentParser):
    debug_options = parser.add_argument_group("Debug")
    debug_options.add_argument(
        "--debug",
        action="store_true",
    )
    debug_options.add_argument(
        "--debug-precision",
        type=int,
        default=4,
    )


def output_args(parser: ArgumentParser):
    output_options = parser.add_argument_group("Output Options")

    output_options.add_argument(
        "--output",
        "-o",
        metavar="PATH",
        required=True,
        type=str,
    )
    output_options.add_argument(
        "--output-png",
        action="store_true",
    )


def main_maker(boxType) -> Callable:
    def main(argv: Sequence[str] | None = None) -> int:
        import argparse

        parser = argparse.ArgumentParser()

        debug_args(parser)
        boxType.add_arguments(parser)
        Dasher.add_arguments(parser)
        output_args(parser)

        args = parser.parse_args(argv)

        # # # # # # # # # # # # # # # # # # # # # # # # # #

        d = Dasher.from_args(
            dimension_scale=300,
            parsed_arguments=args,
        )

        the_box = boxType.from_args(
            origin=Point(0, 0),
            dimension_scale=300,
            dasher=d,
            parsed_arguments=args,
        )

        drawing = drawsvg.Drawing(
            width="100%",
            height="100%",
            viewBox="0 -1800 3600 3600",
            transform="scale(300)",
        )

        drawing.append(the_box.draw())
        drawing.save_svg(f"{args.output}.svg")
        return 0

    return main


ElephantBoxMain = main_maker(ElephantBox)
