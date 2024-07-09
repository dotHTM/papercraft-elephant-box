from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Callable
from collections.abc import Sequence

import drawsvg

from elephantbox.boxes.component.Dash import Dasher
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


def main_maker(
    boxType, origin: Point = Point(0, 0), laser_bed: Point = Point(3600, 3600)
) -> Callable:
    def main(argv: Sequence[str] | None = None) -> int:
        import argparse

        parser = argparse.ArgumentParser()

        debug_args(parser)
        parser.add_argument("--whole-rotate", type=float, default=0)
        parser.add_argument("--draw-laser-bed", action="store_true")
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
            viewBox=f"{origin.x} {origin.y} {laser_bed.x} {laser_bed.y}",
            transform="scale(300)",
        )

        if args.draw_laser_bed:
            drawing.append(
                drawsvg.Rectangle(
                    *origin.tuple,
                    *laser_bed.tuple,
                    stroke="orange",
                    stroke_width=3,
                    fill="orange",
                    opacity="25%",
                )
            )

        grp = drawsvg.Group(transform=f"rotate({args.whole_rotate})")

        grp.append(the_box.draw())
        drawing.append(grp)
        drawing.save_svg(f"{args.output}.svg")
        return 0

    return main
