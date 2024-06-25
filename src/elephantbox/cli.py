from __future__ import annotations

from math import atan, ceil, cos, sin, sqrt
from typing import NamedTuple, Optional, Sequence

import drawsvg as draw
import logging

import random
from pprint import pformat


class UNITS(NamedTuple):
    DPI = 300

    INCH = DPI
    CM = INCH / 2.54
    MM = INCH / 25.4
    POINT = 1


class DEFAULTS(NamedTuple):
    LASER_BED_WIDTH = 12 * UNITS.INCH
    LASER_BED_HEIGHT = 12 * UNITS.INCH
    BOTTOM_WIDTH = 2.5 * UNITS.INCH
    BOTTOM_HEIGHT = 3.5 * UNITS.INCH
    BOTTOM_WIGGLE = 0.1 * UNITS.INCH
    BOX_TALL = 1.5 * UNITS.INCH
    CORNER_SAVER = 0.125 * UNITS.INCH
    CARDSTOCK_THICKNESS = 0.05 * UNITS.INCH
    FLAP_THICKNESS = 1 * UNITS.INCH
    NOSE_WIDTH = 1.5 * UNITS.INCH
    MAX_DASH_LENGTH = 1 / 30 * UNITS.INCH
    DASH_PERIOD = 1 / 5 * UNITS.INCH

    DEBUG_OFFSET = 0.2 * UNITS.INCH

    # Stroke
    STROKE_WIDTH = 4

    DASH_STROKE = STROKE_WIDTH
    DASH_COLOR = "red"

    OUTER_CUT_COLOR = "green"
    OUTER_CUT_STROKE = STROKE_WIDTH

    INNER_CUT_COLOR = "blue"
    INNER_CUT_STROKE = STROKE_WIDTH


def randColor(lower: int = 0, upper: int = 255):
    r = lambda: random.randint(lower, upper)
    return "#%02X%02X%02X" % (r(), r(), r())


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    # print("\n" * 20)

    parser = argparse.ArgumentParser()
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

    parser.add_argument(
        "--cm",
        action="store_true",
        help="Use centimeters instead of inches.",
    )
    parser.add_argument(
        "--mm",
        action="store_true",
        help="Use millimeters instead of inches.",
    )
    box_dimensions = parser.add_argument_group("Box Dimensions (user units)")
    box_dimensions_points = parser.add_argument_group("Box Dimensions (Points)")

    for p in [
        (("--laser-bed-width", "--lx"), DEFAULTS.LASER_BED_WIDTH, {}),
        (("--laser-bed-height", "--ly"), DEFAULTS.LASER_BED_HEIGHT, {}),
        (
            ("--bottom-wiggle", "-w"),
            DEFAULTS.BOTTOM_WIGGLE,
            {"help": "Wiggle room to increase box bottom by."},
        ),
        (
            ("--bottom-width", "-x"),
            DEFAULTS.BOTTOM_WIDTH,
            {"help": "Size of box interior, x."},
        ),
        (
            ("--bottom-height", "-y"),
            DEFAULTS.BOTTOM_HEIGHT,
            {"help": "Size of box interior, y"},
        ),
        (
            ("--box-tall", "-z"),
            DEFAULTS.BOX_TALL,
            {"help": "Size of box interior, z"},
        ),
        (
            ("--corner-saver", "-s"),
            DEFAULTS.CORNER_SAVER,
            {
                "help": "Perferated fold lines will stop this far away from corners and edges."
            },
        ),
        (
            ("--cardstock-thickness", "-c"),
            DEFAULTS.CARDSTOCK_THICKNESS,
            {
                "help": "Amount to adjust lid size for, given cardstock thickness."
            },
        ),
        (
            ("--flap-thickness", "-f"),
            DEFAULTS.FLAP_THICKNESS,
            {"help": "Lid tuck flap size."},
        ),
        (
            ("--nose-width", "-n"),
            DEFAULTS.NOSE_WIDTH,
            {"help": "Tuck flap tab width."},
        ),
    ]:
        box_dimensions.add_argument(*p[0], metavar="FLOAT", type=float, **p[2])
        box_dimensions_points.add_argument(
            f"{p[0][0]}-points",
            metavar="FLOAT",
            type=float,
            default=p[1],
            **p[2],
        )

    edge_options = parser.add_argument_group("Edge Options")

    edge_options.add_argument(
        "--outer-cut-stroke",
        metavar="FLOAT",
        type=float,
        default=DEFAULTS.OUTER_CUT_STROKE,
    )
    edge_options.add_argument(
        "--outer-cut-color",
        metavar="COLOR NAME | HEX CODE",
        type=str,
        default=DEFAULTS.OUTER_CUT_COLOR,
    )
    edge_options.add_argument(
        "--inner-cut-stroke",
        metavar="FLOAT",
        type=float,
        default=DEFAULTS.INNER_CUT_STROKE,
    )
    edge_options.add_argument(
        "--inner-cut-color",
        metavar="COLOR NAME | HEX CODE",
        type=str,
        default=DEFAULTS.INNER_CUT_COLOR,
    )

    edge_options.add_argument(
        "--max-dash-length-points",
        metavar="FLOAT",
        type=float,
        default=DEFAULTS.MAX_DASH_LENGTH,
    )
    edge_options.add_argument(
        "--max-dash-length",
        "--dl",
        metavar="FLOAT",
        type=float,
    )
    edge_options.add_argument(
        "--dash-period-points",
        metavar="FLOAT",
        type=float,
        default=DEFAULTS.DASH_PERIOD,
    )
    edge_options.add_argument(
        "--dash-period",
        "--dp",
        metavar="FLOAT",
        type=float,
    )

    edge_options.add_argument(
        "--dash-stroke",
        metavar="FLOAT",
        type=float,
        default=DEFAULTS.DASH_STROKE,
    )
    edge_options.add_argument(
        "--dash-color",
        metavar="COLOR NAME | HEX CODE",
        type=str,
        default=DEFAULTS.DASH_COLOR,
    )

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

    args = parser.parse_args(argv)

    debug_precision = f" {args.debug_precision+5}.{args.debug_precision}f"

    logging.basicConfig(
        format="%(levelname)s %(asctime)s | %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
    )

    # Constant

    unit = UNITS.INCH
    unit_name = "inch"
    if args.cm:
        logging.info("Using metric (cm).")
        unit_name = "cm"
        unit = UNITS.CM
    if args.mm:
        logging.info("Using metric (mm).")
        unit_name = "mm"
        unit = UNITS.MM

    sqrt2over2 = sqrt(2) / 2
    # re-establish

    for key in [
        "laser_bed_width",
        "laser_bed_height",
        "bottom_width",
        "bottom_height",
        "bottom_wiggle",
        "box_tall",
        "corner_saver",
        "cardstock_thickness",
        "flap_thickness",
        "nose_width",
        "max_dash_length",
        "dash_period",
    ]:
        if hasattr(args, key) and getattr(args, key) is not None:
            setattr(args, f"{key}_points", getattr(args, key) * unit)

    # Defined

    BottomWellWidth_Pt = args.bottom_width_points + args.bottom_wiggle_points
    BottomWellHeight_Pt = args.bottom_height_points + args.bottom_wiggle_points
    DeckThickness_Pt = args.box_tall_points
    CornerSaver_Pt = args.corner_saver_points
    CardstockThickness_Pt = args.cardstock_thickness_points
    FlapThickness_Pt = args.flap_thickness_points
    NoseWidth_Pt = args.nose_width_points

    # Calculated

    def EarWidth_Pt():
        return BottomWellWidth_Pt - CardstockThickness_Pt

    def HeadWidth_Pt():
        return BottomWellWidth_Pt + CardstockThickness_Pt

    def HeadHeight_Pt():
        return BottomWellHeight_Pt - CardstockThickness_Pt

    def NasalLabia_Pt():
        return (HeadHeight_Pt() - 2 * FlapThickness_Pt - NoseWidth_Pt) / 2

    def DiagonalDeckThickness_Pt():
        return DeckThickness_Pt * sqrt2over2

    def DiagonalCornerSaver_Pt():
        return CornerSaver_Pt * sqrt2over2

    def NeckBase_Pt():
        return CardwellVerticalRails[9]

    def EarStart_Pt():
        return NeckBase_Pt() + CardstockThickness_Pt

    def NoseStart_Pt():
        return NeckBase_Pt() + HeadWidth_Pt() + FlapThickness_Pt

    def RearEarRadius_Pt():
        return FlapThickness_Pt / 2

    def NoseTipEnd_Pt():
        return (
            NeckBase_Pt()
            + HeadWidth_Pt()
            + FlapThickness_Pt * 2
            + NoseWidth_Pt / 2
        )

    # Checks

    if DeckThickness_Pt < FlapThickness_Pt:
        logging.warn("DeckThickness_Pt < FlapThickness_Pt")
        logging.warn("   setting equal")
        FlapThickness_Pt = DeckThickness_Pt

    if EarWidth_Pt() < FlapThickness_Pt * 1.5:
        logging.warn("EarWidth_Pt() < FlapThickness_Pt *1.5")
        logging.warn("   attempting to correct")
        FlapThickness_Pt = EarWidth_Pt() / 1.5

    if HeadHeight_Pt() < 2 * FlapThickness_Pt + NoseWidth_Pt:
        logging.warn(
            "FlapThickness_Pt + NoseWidth_Pt too large for HeadHeight_Pt"
        )
        logging.warn("   attempting to correct")
        FlapThickness_Pt = (HeadHeight_Pt() - NoseWidth_Pt) / 2

    if NasalLabia_Pt() < 0:
        logging.warn(f"Negative {NasalLabia_Pt()/unit=}.")

    if NoseWidth_Pt < 0:
        logging.warn(f"NoseWidth_Pt negative {NoseWidth_Pt/unit=}.")

    if NoseWidth_Pt < 2 * CornerSaver_Pt:
        logging.warn(f"NoseWidth_Pt smaller than {CornerSaver_Pt/unit=}.")

    CardwellVerticalRails = [
        0,  #                                                   0 -
        CornerSaver_Pt,  #                                         1
        DeckThickness_Pt - CornerSaver_Pt,  #                         2
        DeckThickness_Pt,  #                                       3 -
        DeckThickness_Pt + CornerSaver_Pt,  #                         4
        DeckThickness_Pt + BottomWellWidth_Pt - CornerSaver_Pt,  #         5
        DeckThickness_Pt + BottomWellWidth_Pt,  #                       6 -
        DeckThickness_Pt + BottomWellWidth_Pt + CornerSaver_Pt,  #         7
        DeckThickness_Pt * 2 + BottomWellWidth_Pt - CornerSaver_Pt,  #     8
        DeckThickness_Pt * 2 + BottomWellWidth_Pt,  #                   9 -
    ]

    CardwellHorizontalRails = [
        -(BottomWellHeight_Pt / 2 + DeckThickness_Pt),  #                0 -
        -(BottomWellHeight_Pt / 2 + DeckThickness_Pt - CornerSaver_Pt),  #  1
        -(BottomWellHeight_Pt / 2 + CornerSaver_Pt),  #                  2
        -(BottomWellHeight_Pt / 2),  #                                3 -
        -(BottomWellHeight_Pt / 2 - CornerSaver_Pt),  #                  4
        (BottomWellHeight_Pt / 2 - CornerSaver_Pt),  #                   5
        (BottomWellHeight_Pt / 2),  #                                 6 -
        (BottomWellHeight_Pt / 2 + CornerSaver_Pt),  #                   7
        (BottomWellHeight_Pt / 2 + DeckThickness_Pt - CornerSaver_Pt),  #   8
        (BottomWellHeight_Pt / 2 + DeckThickness_Pt),  #                 9 -
    ]

    def DiagonalTopLeft():
        return (
            (CardwellVerticalRails[3] - DiagonalDeckThickness_Pt()),
            (CardwellHorizontalRails[3] - DiagonalDeckThickness_Pt()),
        )

    def DiagonalBottomRightNose():
        return (
            NoseTipEnd_Pt() + (NoseWidth_Pt / 2) * (sqrt2over2 - 1),
            NoseWidth_Pt * sqrt(2) / 4,
        )

    def DiagonalBottomRightFace():
        return (
            EarStart_Pt() + EarWidth_Pt() + FlapThickness_Pt * (sqrt2over2),
            HeadHeight_Pt() / 2 - FlapThickness_Pt * (1 - sqrt2over2),
        )

    def DiagonalBottomRightEar():
        return (
            EarStart_Pt() + EarWidth_Pt() - FlapThickness_Pt * (1 - sqrt2over2),
            HeadHeight_Pt() / 2 + FlapThickness_Pt * (sqrt2over2),
        )

    def PointRotatedSize(x2, y2):
        (x1, y1) = DiagonalTopLeft()
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return (dx + dy) * sqrt2over2

    def RotatedSize():
        return max(
            [
                PointRotatedSize(*DiagonalBottomRightNose()),
                PointRotatedSize(*DiagonalBottomRightFace()),
                PointRotatedSize(*DiagonalBottomRightEar()),
            ]
        )

    stats = {
        "BottomWellWidth_Pt           ": f"{BottomWellWidth_Pt / unit:{debug_precision}} {unit_name}",
        "BottomWellHeight_Pt          ": f"{BottomWellHeight_Pt / unit:{debug_precision}} {unit_name}",
        "DeckThickness_Pt             ": f"{DeckThickness_Pt / unit:{debug_precision}} {unit_name}",
        "CornerSaver_Pt               ": f"{CornerSaver_Pt / unit:{debug_precision}} {unit_name}",
        "CardstockThickness_Pt        ": f"{CardstockThickness_Pt / unit:{debug_precision}} {unit_name}",
        "FlapThickness_Pt             ": f"{FlapThickness_Pt / unit:{debug_precision}} {unit_name}",
        "NoseWidth_Pt                 ": f"{NoseWidth_Pt / unit:{debug_precision}} {unit_name}",
        "args.laser_bed_width_points  ": args.laser_bed_width_points,
        "args.laser_bed_height_points ": args.laser_bed_height_points,
        "---------------------------- ": "-------------------",
        "DiagonalCornerSaver_Pt()     ": f"{DiagonalCornerSaver_Pt() / unit:{debug_precision}} {unit_name}",
        "DiagonalDeckThickness_Pt()   ": f"{DiagonalDeckThickness_Pt() / unit:{debug_precision}} {unit_name}",
        "EarStart_Pt()                ": f"{EarStart_Pt() / unit:{debug_precision}} {unit_name}",
        "EarWidth_Pt()                ": f"{EarWidth_Pt() / unit:{debug_precision}} {unit_name}",
        "HeadHeight_Pt()              ": f"{HeadHeight_Pt() / unit:{debug_precision}} {unit_name}",
        "HeadWidth_Pt()               ": f"{HeadWidth_Pt() / unit:{debug_precision}} {unit_name}",
        "NasalLabia_Pt()              ": f"{NasalLabia_Pt() / unit:{debug_precision}} {unit_name}",
        "NeckBase_Pt()                ": f"{NeckBase_Pt() / unit:{debug_precision}} {unit_name}",
        "NoseStart_Pt()               ": f"{NoseStart_Pt() / unit:{debug_precision}} {unit_name}",
        "DiagonalTopLeft() x          ": f"{DiagonalTopLeft()[0] / unit:{debug_precision}} {unit_name}",
        "DiagonalTopLeft() y          ": f"{DiagonalTopLeft()[1] / unit:{debug_precision}} {unit_name}",
        "=--------------------------- ": "-------------------",
        "DiagonalBottomRightNose() x  ": f"{DiagonalBottomRightNose()[0] / unit:{debug_precision}} {unit_name}",
        "DiagonalBottomRightNose() y  ": f"{DiagonalBottomRightNose()[1] / unit:{debug_precision}} {unit_name}",
        "==-------------------------- ": "-------------------",
        "DiagonalBottomRightFace() x  ": f"{DiagonalBottomRightFace()[0] / unit:{debug_precision}} {unit_name}",
        "DiagonalBottomRightFace() y  ": f"{DiagonalBottomRightFace()[1] / unit:{debug_precision}} {unit_name}",
        "=-=------------------------- ": "-------------------",
        "DiagonalBottomRightEar() x   ": f"{DiagonalBottomRightEar()[0] / unit:{debug_precision}} {unit_name}",
        "DiagonalBottomRightEar() y   ": f"{DiagonalBottomRightEar()[1] / unit:{debug_precision}} {unit_name}",
        "==-=------------------------ ": "-------------------",
        "NoseTipEnd_Pt()              ": f"{NoseTipEnd_Pt() / unit:{debug_precision}} {unit_name}",
        "RotatedSize()                ": f"{RotatedSize() / unit:{debug_precision}} {unit_name}",
    }

    if args.laser_bed_width_points < NoseTipEnd_Pt():
        logging.warn("Nose outside of bounds")
        if RotatedSize() < args.laser_bed_width_points:
            logging.info("  Might fit width rotated 45 degrees")
        if RotatedSize() < args.laser_bed_height_points:
            logging.info("  Might fit height rotated 45 degrees")

    logging.debug(f"\n{pformat(stats, sort_dicts=False, indent=2)}")

    OuterBoundsWidth = max([args.laser_bed_width_points, NoseTipEnd_Pt()])
    OuterBoundsHeight = max(
        [
            args.laser_bed_height_points,
            (BottomWellHeight_Pt / 2 + DeckThickness_Pt),
        ]
    )

    logging.info(
        f"( {OuterBoundsWidth/unit:{debug_precision}} {unit_name}, {OuterBoundsHeight/unit:{debug_precision}} {unit_name} ), {NoseTipEnd_Pt()/unit:{debug_precision}} {unit_name}, {RotatedSize()/unit:{debug_precision}} {unit_name}"
    )

    drawing = draw.Drawing(
        *("100%", "100%"),
        viewBox=f"{0} {-(OuterBoundsHeight / 2)} {OuterBoundsWidth} {OuterBoundsHeight}",
    )

    def rect(x1, y1, x2, y2, color):
        (x, y, w, h) = (x1, y1, x2 - x1, y2 - y1)
        # print("rect", x, y, w, h)
        return draw.Rectangle(x, y, w, h, fill=color, stroke="black")

    def dasher(
        start: tuple[float, float],
        end: tuple[float, float],
        max_dash_length: float,
        period: float,
    ) -> list:
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if dx == 0:
            # logging.warn("Bailing out for divide by zero")
            dx = 0.00001
            # return []
        direction = atan(dy / dx)

        actual_length = sqrt(pow(dx, 2) + pow(dy, 2))

        period_count = ceil((actual_length - max_dash_length) / period)
        max_length = max_dash_length + period_count * period
        scale_factor = actual_length / max_length
        actual_dash_length = max_dash_length * scale_factor
        actual_period = period * scale_factor

        adl_x = actual_dash_length * cos(direction)
        adl_y = actual_dash_length * sin(direction)

        ap_x = actual_period * cos(direction)
        ap_y = actual_period * sin(direction)

        dashes = []
        # print("+++++++")
        for n in range(period_count + 1):
            this_dash_start_x = start[0] + n * ap_x
            this_dash_start_y = start[1] + n * ap_y
            this_dash_end_x = this_dash_start_x + adl_x
            this_dash_end_y = this_dash_start_y + adl_y

            # print(
            #     this_dash_start_x,
            #     this_dash_start_y,
            #     this_dash_end_x,
            #     this_dash_end_y,
            # )

            dashes.append(
                draw.Line(
                    this_dash_start_x,
                    this_dash_start_y,
                    this_dash_end_x,
                    this_dash_end_y,
                    stroke=args.dash_color,
                    stroke_width=args.dash_stroke,
                )
            )

        return dashes

    def randFillAttrs():
        return {
            "stroke": "black",
            "fill": randColor(192),
        }

    def guideGrid():
        # Laser Bed
        drawing.append(
            draw.Rectangle(
                0,
                -args.laser_bed_height_points / 2,
                args.laser_bed_width_points,
                args.laser_bed_height_points,
                **randFillAttrs(),
            )
        )

        # # Body
        lvr = None
        for vr in CardwellVerticalRails:
            lhr = None
            for hr in CardwellHorizontalRails:
                if lvr is not None and lhr is not None:
                    drawing.append(rect(lvr, lhr, vr, hr, randColor(lower=192)))
                    pass
                lhr = hr
            lvr = vr

        # # Head
        drawing.append(
            draw.Rectangle(
                NeckBase_Pt(),
                -HeadHeight_Pt() / 2,
                HeadWidth_Pt(),
                HeadHeight_Pt(),
                **randFillAttrs(),
            )
        )

        # # Top Ear
        drawing.append(
            draw.Rectangle(
                EarStart_Pt(),
                -HeadHeight_Pt() / 2 - FlapThickness_Pt,
                EarWidth_Pt(),
                FlapThickness_Pt,
                **randFillAttrs(),
            )
        )

        # # Bottom Ear
        drawing.append(
            draw.Rectangle(
                EarStart_Pt(),
                HeadHeight_Pt() / 2,
                EarWidth_Pt(),
                FlapThickness_Pt,
                **randFillAttrs(),
            )
        )

        # # Face Flap
        drawing.append(
            draw.Rectangle(
                NeckBase_Pt() + HeadWidth_Pt(),
                -HeadHeight_Pt() / 2,
                FlapThickness_Pt,
                HeadHeight_Pt(),
                **randFillAttrs(),
            )
        )

        # # Nose Segment
        drawing.append(
            draw.Rectangle(
                NoseStart_Pt(),
                -NoseWidth_Pt / 2,
                FlapThickness_Pt,
                NoseWidth_Pt,
                **randFillAttrs(),
            )
        )

        # # Nose Tip
        drawing.append(
            draw.Rectangle(
                NoseStart_Pt() + FlapThickness_Pt,
                -NoseWidth_Pt / 2,
                NoseWidth_Pt / 2,
                NoseWidth_Pt,
                **randFillAttrs(),
            )
        )

    def cutOuterLine():
        cutPath = draw.Path(
            fill="#eeeeffa0",
            stroke=args.outer_cut_color,
            stroke_width=args.outer_cut_stroke,
        )

        # # Body
        (
            cutPath.M(CardwellVerticalRails[9], CardwellHorizontalRails[3])
            .A(
                *(DeckThickness_Pt, DeckThickness_Pt),
                *(0, 0, 0),
                *(CardwellVerticalRails[6], CardwellHorizontalRails[0]),
            )
            .H(CardwellVerticalRails[3])
            .A(
                *(DeckThickness_Pt, DeckThickness_Pt),
                *(0, 0, 0),
                *(CardwellVerticalRails[0], CardwellHorizontalRails[3]),
            )
            .L(CardwellVerticalRails[0], CardwellHorizontalRails[6])
            .A(
                *(DeckThickness_Pt, DeckThickness_Pt),
                *(0, 0, 0),
                *(CardwellVerticalRails[3], CardwellHorizontalRails[9]),
            )
            .L(CardwellVerticalRails[6], CardwellHorizontalRails[9])
            .A(
                *(DeckThickness_Pt, DeckThickness_Pt),
                *(0, 0, 0),
                *(CardwellVerticalRails[9], CardwellHorizontalRails[6]),
            )
        )

        # head
        (
            cutPath.L(NeckBase_Pt(), HeadHeight_Pt() / 2)
            ##
            .L(
                EarStart_Pt(),
                HeadHeight_Pt() / 2,
            )
            .v(RearEarRadius_Pt())
            .a(
                *(RearEarRadius_Pt(), RearEarRadius_Pt()),
                *(0, 0, 0),
                *(RearEarRadius_Pt(), RearEarRadius_Pt()),
            )
            .h(EarWidth_Pt() - FlapThickness_Pt * 3 / 2)
            .a(
                *(FlapThickness_Pt, FlapThickness_Pt),
                *(0, 0, 0),
                *(FlapThickness_Pt, -FlapThickness_Pt),
            )
            .h(CardstockThickness_Pt)
            .a(
                *(FlapThickness_Pt, FlapThickness_Pt),
                *(0, 0, 0),
                *(FlapThickness_Pt, -FlapThickness_Pt),
            )
            .v(-NasalLabia_Pt())
            .h(FlapThickness_Pt)
            .a(
                *(NoseWidth_Pt / 2, NoseWidth_Pt / 2),
                *(0, 0, 0),
                *(0, -NoseWidth_Pt),
            )
            .h(-FlapThickness_Pt)
            .v(-NasalLabia_Pt())
            .a(
                *(FlapThickness_Pt, FlapThickness_Pt),
                *(0, 0, 0),
                *(-FlapThickness_Pt, -FlapThickness_Pt),
            )
            .h(-CardstockThickness_Pt)
            .a(
                *(FlapThickness_Pt, FlapThickness_Pt),
                *(0, 0, 0),
                *(-FlapThickness_Pt, -FlapThickness_Pt),
            )
            .h(-(EarWidth_Pt() - FlapThickness_Pt * 3 / 2))
            .a(
                *(RearEarRadius_Pt(), RearEarRadius_Pt()),
                *(0, 0, 0),
                *(-RearEarRadius_Pt(), RearEarRadius_Pt()),
            )
            .L(
                EarStart_Pt(),
                -HeadHeight_Pt() / 2,
            )
            ##
            .L(NeckBase_Pt(), -HeadHeight_Pt() / 2)
        )

        # close off
        cutPath.Z()

        drawing.append(cutPath)

    def foldLines():
        foldList: list[tuple[tuple, tuple]] = [
            (
                (
                    CardwellVerticalRails[3]
                    - DiagonalDeckThickness_Pt()
                    + DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[3]
                    - DiagonalDeckThickness_Pt()
                    + DiagonalCornerSaver_Pt(),
                ),
                (
                    CardwellVerticalRails[3] - DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[3] - DiagonalCornerSaver_Pt(),
                ),
            ),
            (
                (
                    CardwellVerticalRails[3]
                    - DiagonalDeckThickness_Pt()
                    + DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[6]
                    + DiagonalDeckThickness_Pt()
                    - DiagonalCornerSaver_Pt(),
                ),
                (
                    CardwellVerticalRails[3] - DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[6] + DiagonalCornerSaver_Pt(),
                ),
            ),
            # # # # # # #
            (
                (
                    CardwellVerticalRails[6] + DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[3] - DiagonalCornerSaver_Pt(),
                ),
                (
                    CardwellVerticalRails[6]
                    + DiagonalDeckThickness_Pt()
                    - DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[3]
                    - DiagonalDeckThickness_Pt()
                    + DiagonalCornerSaver_Pt(),
                ),
            ),
            (
                (
                    CardwellVerticalRails[6] + DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[6] + DiagonalCornerSaver_Pt(),
                ),
                (
                    CardwellVerticalRails[6]
                    + DiagonalDeckThickness_Pt()
                    - DiagonalCornerSaver_Pt(),
                    CardwellHorizontalRails[6]
                    + DiagonalDeckThickness_Pt()
                    - DiagonalCornerSaver_Pt(),
                ),
            ),
            # # # #
            (
                (CardwellVerticalRails[3], CardwellHorizontalRails[1]),
                (CardwellVerticalRails[3], CardwellHorizontalRails[2]),
            ),
            (
                (CardwellVerticalRails[3], CardwellHorizontalRails[4]),
                (CardwellVerticalRails[3], CardwellHorizontalRails[5]),
            ),
            (
                (CardwellVerticalRails[3], CardwellHorizontalRails[7]),
                (CardwellVerticalRails[3], CardwellHorizontalRails[8]),
            ),
            (
                (CardwellVerticalRails[6], CardwellHorizontalRails[1]),
                (CardwellVerticalRails[6], CardwellHorizontalRails[2]),
            ),
            (
                (CardwellVerticalRails[6], CardwellHorizontalRails[4]),
                (CardwellVerticalRails[6], CardwellHorizontalRails[5]),
            ),
            (
                (CardwellVerticalRails[6], CardwellHorizontalRails[7]),
                (CardwellVerticalRails[6], CardwellHorizontalRails[8]),
            ),
            (
                (CardwellVerticalRails[1], CardwellHorizontalRails[3]),
                (CardwellVerticalRails[2], CardwellHorizontalRails[3]),
            ),
            (
                (CardwellVerticalRails[4], CardwellHorizontalRails[3]),
                (CardwellVerticalRails[5], CardwellHorizontalRails[3]),
            ),
            (
                (CardwellVerticalRails[7], CardwellHorizontalRails[3]),
                (CardwellVerticalRails[8], CardwellHorizontalRails[3]),
            ),
            (
                (CardwellVerticalRails[1], CardwellHorizontalRails[6]),
                (CardwellVerticalRails[2], CardwellHorizontalRails[6]),
            ),
            (
                (CardwellVerticalRails[4], CardwellHorizontalRails[6]),
                (CardwellVerticalRails[5], CardwellHorizontalRails[6]),
            ),
            (
                (CardwellVerticalRails[7], CardwellHorizontalRails[6]),
                (CardwellVerticalRails[8], CardwellHorizontalRails[6]),
            ),
            #
            (
                (NeckBase_Pt(), CardwellHorizontalRails[4]),
                (NeckBase_Pt(), CardwellHorizontalRails[5]),
            ),
            # # Ear flaps
            (
                (
                    NeckBase_Pt() + CardstockThickness_Pt + CornerSaver_Pt,
                    -HeadHeight_Pt() / 2,
                ),
                (
                    NeckBase_Pt()
                    + CardstockThickness_Pt
                    - CornerSaver_Pt
                    + EarWidth_Pt(),
                    -HeadHeight_Pt() / 2,
                ),
            ),
            (
                (
                    NeckBase_Pt() + CardstockThickness_Pt + CornerSaver_Pt,
                    HeadHeight_Pt() / 2,
                ),
                (
                    NeckBase_Pt()
                    + CardstockThickness_Pt
                    - CornerSaver_Pt
                    + EarWidth_Pt(),
                    HeadHeight_Pt() / 2,
                ),
            ),
            # nose
            (
                (
                    NeckBase_Pt()
                    + 2 * CardstockThickness_Pt
                    + EarWidth_Pt()
                    + FlapThickness_Pt,
                    (NoseWidth_Pt / 2 - CornerSaver_Pt),
                ),
                (
                    NeckBase_Pt()
                    + 2 * CardstockThickness_Pt
                    + EarWidth_Pt()
                    + FlapThickness_Pt,
                    -(NoseWidth_Pt / 2 - CornerSaver_Pt),
                ),
            ),
            (
                (
                    NeckBase_Pt()
                    + 2 * CardstockThickness_Pt
                    + EarWidth_Pt()
                    + 2 * FlapThickness_Pt,
                    (NoseWidth_Pt / 2 - CornerSaver_Pt),
                ),
                (
                    NeckBase_Pt()
                    + 2 * CardstockThickness_Pt
                    + EarWidth_Pt()
                    + 2 * FlapThickness_Pt,
                    -(NoseWidth_Pt / 2 - CornerSaver_Pt),
                ),
            ),
        ]

        if 0 < HeadHeight_Pt() - NoseWidth_Pt - 2 * CornerSaver_Pt:
            foldList.extend(
                [
                    # Face flap
                    (
                        (
                            NeckBase_Pt() + HeadWidth_Pt(),
                            (HeadHeight_Pt() / 2 - CornerSaver_Pt),
                        ),
                        (
                            NeckBase_Pt() + HeadWidth_Pt(),
                            (NoseWidth_Pt / 2 + CornerSaver_Pt),
                        ),
                    ),
                    (
                        (
                            NeckBase_Pt() + HeadWidth_Pt(),
                            -(NoseWidth_Pt / 2 + CornerSaver_Pt),
                        ),
                        (
                            NeckBase_Pt() + HeadWidth_Pt(),
                            -(HeadHeight_Pt() / 2 - CornerSaver_Pt),
                        ),
                    ),
                ]
            )

        for fl in foldList:
            foldLine = draw.Path(
                # stroke=randColor(),
                stroke=args.dash_color,
                stroke_width=args.dash_stroke,
            )
            foldLine.M(*fl[0]).L(*fl[1])
            # drawing.append(foldLine)
            for d in dasher(
                *fl,
                args.max_dash_length_points,
                args.dash_period_points,
            ):
                drawing.append(d)

    def cutInnerlines():
        cutList = [
            (
                (
                    NeckBase_Pt() + HeadWidth_Pt(),
                    (NoseWidth_Pt / 2),
                ),
                (
                    NeckBase_Pt() + HeadWidth_Pt(),
                    -(NoseWidth_Pt / 2),
                ),
            )
        ]

        for cl in cutList:
            foldLine = draw.Path(
                stroke=args.inner_cut_color,
                stroke_width=args.inner_cut_stroke,
            )
            foldLine.M(*cl[0]).L(*cl[1])
            drawing.append(foldLine)

    if args.debug:
        guideGrid()
    cutOuterLine()
    foldLines()
    cutInnerlines()

    if args.debug:
        offset = DEFAULTS.DEBUG_OFFSET

        def distance_line(
            x1,
            y1,
            x2,
            y2,
            x3=None,
            y3=None,
            theme1="cyan",
            theme2="skyblue",
            theme3="blue",
            theme4="navy",
        ):
            distance = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))

            for p in [(x1, y1), (x2, y2)]:
                drawing.append(
                    draw.Circle(
                        *p,
                        offset / 2,
                        stroke=theme4,
                        stroke_width=10,
                        fill=theme2,
                    )
                )
            drawing.append(
                draw.Line(
                    x1,
                    y1,
                    x2,
                    y2,
                    stroke=theme1,
                    stroke_width=10,
                )
            )

            drawing.append(
                draw.Text(
                    f"{distance/unit:{debug_precision}}",
                    96,
                    x2 + offset,
                    y2 + offset,
                    fill=theme3,
                )
            )
            if x3 is not None and y3 is not None:
                drawing.append(
                    draw.Line(
                        x1,
                        y1,
                        x3,
                        y3,
                        stroke=theme1,
                        stroke_width=10,
                    )
                )

        dTopLeft = DiagonalTopLeft()

        drawing.append(
            draw.Circle(
                *dTopLeft,
                offset / 2,
                stroke="black",
                stroke_width=10,
                fill="darkslategrey",
            )
        )

        dNose = DiagonalBottomRightNose()
        dNoseLength = PointRotatedSize(*dNose)
        dFace = DiagonalBottomRightFace()
        dFaceLength = PointRotatedSize(*dFace)
        dEar = DiagonalBottomRightEar()
        dEarLength = PointRotatedSize(*dEar)

        angleTheme = ("cyan", "mediumslateblue", "navy", "blue")
        orthoTheme = ("lime", "mediumseagreen", "forestgreen", "seagreen")
        nonePoint = (None, None)

        for l in [
            (0, 0, NoseTipEnd_Pt(), 0, *nonePoint, *orthoTheme),
            (
                dNose[0] - dNoseLength * sqrt2over2,
                dNose[1] - dNoseLength * sqrt2over2,
                *dNose,
                *dTopLeft,
                *angleTheme,
            ),
            (
                dFace[0] - dFaceLength * sqrt2over2,
                dFace[1] - dFaceLength * sqrt2over2,
                *dFace,
                *dTopLeft,
                *angleTheme,
            ),
            (
                dEar[0] - dEarLength * sqrt2over2,
                dEar[1] - dEarLength * sqrt2over2,
                *dEar,
                *dTopLeft,
                *angleTheme,
            ),
            (
                DeckThickness_Pt + BottomWellWidth_Pt / 2,
                CardwellHorizontalRails[0],
                DeckThickness_Pt + BottomWellWidth_Pt / 2,
                CardwellHorizontalRails[9],
                *nonePoint,
                *orthoTheme,
            ),
            (
                NeckBase_Pt() + HeadWidth_Pt() / 2,
                -(HeadHeight_Pt() / 2 + FlapThickness_Pt),
                NeckBase_Pt() + HeadWidth_Pt() / 2,
                (HeadHeight_Pt() / 2 + FlapThickness_Pt),
                *nonePoint,
                *orthoTheme,
            ),
        ]:
            distance_line(*l)

    if args.output_png:
        drawing.set_pixel_scale(1)
        drawing.save_png(f"{args.output}.png")
    drawing.save_svg(f"{args.output}.svg")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
