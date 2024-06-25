from __future__ import annotations

from math import atan, ceil, cos, sin, sqrt
from typing import NamedTuple, Optional, Sequence

import drawsvg as draw
import logging

import random
from pprint import pformat


class DEFAULTS(NamedTuple):
    LASER_BED_WIDTH = 12
    LASER_BED_HEIGHT = 12
    CARD_WIDTH = 2.5
    CARD_HEIGHT = 3.5
    CARD_WIGGLE = 0.1
    DECK_THICKNESS = 1.75
    CORNER_SAVER = 0.125
    SLIVER = 0.05
    FLAP_THICKNESS = 1
    NOSE_WIDTH = 1.5
    MAX_DASH_LENGTH = 1 / 25
    DASH_PERIOD = 1 / 5


def randColor(lower: int = 0, upper: int = 255):
    r = lambda: random.randint(lower, upper)
    return "#%02X%02X%02X" % (r(), r(), r())


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    print("\n" * 20)

    logging.basicConfig(
        format="%(levelname)s %(asctime)s | %(message)s", level=logging.INFO
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--laser-bed-width",
        type=float,
        default=DEFAULTS.LASER_BED_WIDTH,
    )
    parser.add_argument(
        "--laser-bed-height",
        type=float,
        default=DEFAULTS.LASER_BED_HEIGHT,
    )

    parser.add_argument(
        "--card-width",
        type=float,
        default=DEFAULTS.CARD_WIDTH,
    )
    parser.add_argument(
        "--card-height",
        type=float,
        default=DEFAULTS.CARD_HEIGHT,
    )
    parser.add_argument(
        "--card-wiggle",
        type=float,
        default=DEFAULTS.CARD_WIGGLE,
    )
    parser.add_argument(
        "--deck-thickness",
        type=float,
        default=DEFAULTS.DECK_THICKNESS,
    )
    parser.add_argument(
        "--corner-saver",
        type=float,
        default=DEFAULTS.CORNER_SAVER,
    )
    parser.add_argument(
        "--sliver",
        type=float,
        default=DEFAULTS.SLIVER,
    )
    parser.add_argument(
        "--flap-thickness",
        type=float,
        default=DEFAULTS.FLAP_THICKNESS,
    )
    parser.add_argument(
        "--nose-width",
        type=float,
        default=DEFAULTS.NOSE_WIDTH,
    )

    parser.add_argument(
        "--max-dash-length",
        type=float,
        default=DEFAULTS.MAX_DASH_LENGTH,
    )
    parser.add_argument(
        "--dash-period",
        type=float,
        default=DEFAULTS.DASH_PERIOD,
    )

    args = parser.parse_args(argv)

    # Constant
    inch = 72

    # Defined

    CardWellWidth = (args.card_width + args.card_wiggle) * inch
    CardWellHeight = (args.card_height + args.card_wiggle) * inch
    DeckThickness = args.deck_thickness * inch
    CornerSaver = args.corner_saver * inch
    Sliver = args.sliver * inch
    FlapThickness = args.flap_thickness * inch
    NoseWidth = args.nose_width * inch

    # Calculated

    def EarWidth():
        return CardWellWidth - Sliver

    def HeadWidth():
        return CardWellWidth + Sliver

    def HeadHeight():
        return CardWellHeight - Sliver

    def NasalLabia():
        return (HeadHeight() - 2 * FlapThickness - NoseWidth) / 2

    def DiagonalDeckThickness():
        return DeckThickness * sqrt(2) / 2

    def DiagonalCornerSaver():
        return CornerSaver * sqrt(2) / 2

    def NeckBase():
        return CardwellVerticalRails[9]

    def EarStart():
        return NeckBase() + Sliver

    def NoseStart():
        return NeckBase() + HeadWidth() + FlapThickness

    def RearEarRadius():
        return FlapThickness / 2

    def NoseTipEnd():
        return NeckBase() + HeadWidth() + FlapThickness * 2 + NoseWidth / 2

    # Checks

    if DeckThickness < FlapThickness:
        logging.warn("DeckThickness < FlapThickness")
        logging.warn("   setting equal")
        FlapThickness = DeckThickness

    if EarWidth() < FlapThickness * 1.5:
        logging.warn("EarWidth() < FlapThickness *1.5")
        logging.warn("   attempting to correct")
        FlapThickness = EarWidth() / 1.5

    if HeadHeight() < 2 * FlapThickness + NoseWidth:
        logging.warn("FlapThickness + NoseWidth too large for HeadHeight")
        logging.warn("   attempting to correct")
        FlapThickness = (HeadHeight() - NoseWidth) / 2

    if NasalLabia() < 0:
        logging.warn(f"Negative {NasalLabia()/inch=}.")

    if NoseWidth < 0:
        logging.warn(f"NoseWidth negative {NoseWidth/inch=}.")

    if NoseWidth < 2 * CornerSaver:
        logging.warn(f"NoseWidth smaller than {CornerSaver/inch=}.")

    CardwellVerticalRails = [
        0,  #                                                   0 -
        CornerSaver,  #                                         1
        DeckThickness - CornerSaver,  #                         2
        DeckThickness,  #                                       3 -
        DeckThickness + CornerSaver,  #                         4
        DeckThickness + CardWellWidth - CornerSaver,  #         5
        DeckThickness + CardWellWidth,  #                       6 -
        DeckThickness + CardWellWidth + CornerSaver,  #         7
        DeckThickness * 2 + CardWellWidth - CornerSaver,  #     8
        DeckThickness * 2 + CardWellWidth,  #                   9 -
    ]

    CardwellHorizontalRails = [
        -(CardWellHeight / 2 + DeckThickness),  #                0 -
        -(CardWellHeight / 2 + DeckThickness - CornerSaver),  #  1
        -(CardWellHeight / 2 + CornerSaver),  #                  2
        -(CardWellHeight / 2),  #                                3 -
        -(CardWellHeight / 2 - CornerSaver),  #                  4
        (CardWellHeight / 2 - CornerSaver),  #                   5
        (CardWellHeight / 2),  #                                 6 -
        (CardWellHeight / 2 + CornerSaver),  #                   7
        (CardWellHeight / 2 + DeckThickness - CornerSaver),  #   8
        (CardWellHeight / 2 + DeckThickness),  #                 9 -
    ]

    def DiagonalTopLeft():
        return (
            (CardwellVerticalRails[3] - DiagonalDeckThickness()),
            (CardwellHorizontalRails[3] - DiagonalDeckThickness()),
        )

    def DiagonalBottomRight():
        return (
            NoseTipEnd() + (NoseWidth / 2) * (sqrt(2) / 2 - 1),
            NoseWidth * sqrt(2) / 4,
        )

    def RotatedSize():
        (x1, y1) = DiagonalTopLeft()
        (x2, y2) = DiagonalBottomRight()

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        return (dx + dy) * sqrt(2) / 2

    stats = {
        "CardWellWidth           ": CardWellWidth / inch,
        "CardWellHeight          ": CardWellHeight / inch,
        "DeckThickness           ": DeckThickness / inch,
        "CornerSaver             ": CornerSaver / inch,
        "Sliver                  ": Sliver / inch,
        "FlapThickness           ": FlapThickness / inch,
        "NoseWidth               ": NoseWidth / inch,
        "args.laser_bed_width    ": args.laser_bed_width,
        "args.laser_bed_height   ": args.laser_bed_height,
        "=-----------------------": "-------------------",
        "DiagonalCornerSaver()   ": DiagonalCornerSaver() / inch,
        "DiagonalDeckThickness() ": DiagonalDeckThickness() / inch,
        "EarStart()              ": EarStart() / inch,
        "EarWidth()              ": EarWidth() / inch,
        "HeadHeight()            ": HeadHeight() / inch,
        "HeadWidth()             ": HeadWidth() / inch,
        "NasalLabia()            ": NasalLabia() / inch,
        "NeckBase()              ": NeckBase() / inch,
        "NoseStart()             ": NoseStart() / inch,
        "------------------------": "-------------------",
        "NoseTipEnd()            ": NoseTipEnd() / inch,
        "DiagonalTopLeft() x     ": DiagonalTopLeft()[0] / inch,
        "DiagonalTopLeft() y     ": DiagonalTopLeft()[1] / inch,
        "DiagonalBottomRight() x ": DiagonalBottomRight()[0] / inch,
        "DiagonalBottomRight() y ": DiagonalBottomRight()[1] / inch,
        "RotatedSize()           ": RotatedSize() / inch,
    }

    if args.laser_bed_width * inch < NoseTipEnd():
        logging.warn("Nose outside of bounds")
        if RotatedSize() < args.laser_bed_width * inch:
            logging.info("  Might fit width rotated 45 degrees")
        if RotatedSize() < args.laser_bed_height * inch:
            logging.info("  Might fit height rotated 45 degrees")

    logging.debug(f"\n{pformat(stats, sort_dicts=False, indent=2)}")

    OuterBoundsWidth = max([args.laser_bed_width * inch, NoseTipEnd()])
    OuterBoundsHeight = max(
        [args.laser_bed_height * inch, (CardWellHeight / 2 + DeckThickness)]
    )

    logging.info(
        f"( {OuterBoundsWidth/inch}, {OuterBoundsHeight/inch} ), {NoseTipEnd()/inch}, {RotatedSize()/inch}"
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
                    stroke="green",
                    stroke_width=1,
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
                -args.laser_bed_height * inch / 2,
                args.laser_bed_width * inch,
                args.laser_bed_height * inch,
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
                NeckBase(),
                -HeadHeight() / 2,
                HeadWidth(),
                HeadHeight(),
                **randFillAttrs(),
            )
        )

        # # Top Ear
        drawing.append(
            draw.Rectangle(
                EarStart(),
                -HeadHeight() / 2 - FlapThickness,
                EarWidth(),
                FlapThickness,
                **randFillAttrs(),
            )
        )

        # # Bottom Ear
        drawing.append(
            draw.Rectangle(
                EarStart(),
                HeadHeight() / 2,
                EarWidth(),
                FlapThickness,
                **randFillAttrs(),
            )
        )

        # # Face Flap
        drawing.append(
            draw.Rectangle(
                NeckBase() + HeadWidth(),
                -HeadHeight() / 2,
                FlapThickness,
                HeadHeight(),
                **randFillAttrs(),
            )
        )

        # # Nose Segment
        drawing.append(
            draw.Rectangle(
                NoseStart(),
                -NoseWidth / 2,
                FlapThickness,
                NoseWidth,
                **randFillAttrs(),
            )
        )

        # # Nose Tip
        drawing.append(
            draw.Rectangle(
                NoseStart() + FlapThickness,
                -NoseWidth / 2,
                FlapThickness,
                NoseWidth,
                **randFillAttrs(),
            )
        )

    def cutOuterLine():
        cutPath = draw.Path(
            fill="#eeeeffa0",
            stroke="black",
            stroke_width=2,
        )

        # # Body
        (
            cutPath.M(CardwellVerticalRails[9], CardwellHorizontalRails[3])
            .A(
                *(DeckThickness, DeckThickness),
                *(0, 0, 0),
                *(CardwellVerticalRails[6], CardwellHorizontalRails[0]),
            )
            .H(CardwellVerticalRails[3])
            .A(
                *(DeckThickness, DeckThickness),
                *(0, 0, 0),
                *(CardwellVerticalRails[0], CardwellHorizontalRails[3]),
            )
            .L(CardwellVerticalRails[0], CardwellHorizontalRails[6])
            .A(
                *(DeckThickness, DeckThickness),
                *(0, 0, 0),
                *(CardwellVerticalRails[3], CardwellHorizontalRails[9]),
            )
            .L(CardwellVerticalRails[6], CardwellHorizontalRails[9])
            .A(
                *(DeckThickness, DeckThickness),
                *(0, 0, 0),
                *(CardwellVerticalRails[9], CardwellHorizontalRails[6]),
            )
        )

        # head
        (
            cutPath.L(NeckBase(), HeadHeight() / 2)
            ##
            .L(
                EarStart(),
                HeadHeight() / 2,
            )
            .v(RearEarRadius())
            .a(
                *(RearEarRadius(), RearEarRadius()),
                *(0, 0, 0),
                *(RearEarRadius(), RearEarRadius()),
            )
            .h(EarWidth() - FlapThickness * 3 / 2)
            .a(
                *(FlapThickness, FlapThickness),
                *(0, 0, 0),
                *(FlapThickness, -FlapThickness),
            )
            .h(Sliver)
            .a(
                *(FlapThickness, FlapThickness),
                *(0, 0, 0),
                *(FlapThickness, -FlapThickness),
            )
            .v(-NasalLabia())
            .h(FlapThickness)
            .a(
                *(NoseWidth / 2, NoseWidth / 2),
                *(0, 0, 0),
                *(0, -NoseWidth),
            )
            .h(-FlapThickness)
            .v(-NasalLabia())
            .a(
                *(FlapThickness, FlapThickness),
                *(0, 0, 0),
                *(-FlapThickness, -FlapThickness),
            )
            .h(-Sliver)
            .a(
                *(FlapThickness, FlapThickness),
                *(0, 0, 0),
                *(-FlapThickness, -FlapThickness),
            )
            .h(-(EarWidth() - FlapThickness * 3 / 2))
            .a(
                *(RearEarRadius(), RearEarRadius()),
                *(0, 0, 0),
                *(-RearEarRadius(), RearEarRadius()),
            )
            .L(
                EarStart(),
                -HeadHeight() / 2,
            )
            ##
            .L(NeckBase(), -HeadHeight() / 2)
        )

        # close off
        cutPath.Z()

        drawing.append(cutPath)

    def foldLines():
        foldList: list[tuple[tuple, tuple]] = [
            (
                (
                    CardwellVerticalRails[3]
                    - DiagonalDeckThickness()
                    + DiagonalCornerSaver(),
                    CardwellHorizontalRails[3]
                    - DiagonalDeckThickness()
                    + DiagonalCornerSaver(),
                ),
                (
                    CardwellVerticalRails[3] - DiagonalCornerSaver(),
                    CardwellHorizontalRails[3] - DiagonalCornerSaver(),
                ),
            ),
            (
                (
                    CardwellVerticalRails[3]
                    - DiagonalDeckThickness()
                    + DiagonalCornerSaver(),
                    CardwellHorizontalRails[6]
                    + DiagonalDeckThickness()
                    - DiagonalCornerSaver(),
                ),
                (
                    CardwellVerticalRails[3] - DiagonalCornerSaver(),
                    CardwellHorizontalRails[6] + DiagonalCornerSaver(),
                ),
            ),
            # # # # # # #
            (
                (
                    CardwellVerticalRails[6] + DiagonalCornerSaver(),
                    CardwellHorizontalRails[3] - DiagonalCornerSaver(),
                ),
                (
                    CardwellVerticalRails[6]
                    + DiagonalDeckThickness()
                    - DiagonalCornerSaver(),
                    CardwellHorizontalRails[3]
                    - DiagonalDeckThickness()
                    + DiagonalCornerSaver(),
                ),
            ),
            (
                (
                    CardwellVerticalRails[6] + DiagonalCornerSaver(),
                    CardwellHorizontalRails[6] + DiagonalCornerSaver(),
                ),
                (
                    CardwellVerticalRails[6]
                    + DiagonalDeckThickness()
                    - DiagonalCornerSaver(),
                    CardwellHorizontalRails[6]
                    + DiagonalDeckThickness()
                    - DiagonalCornerSaver(),
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
                (NeckBase(), CardwellHorizontalRails[4]),
                (NeckBase(), CardwellHorizontalRails[5]),
            ),
            # # Ear flaps
            (
                (
                    NeckBase() + Sliver + CornerSaver,
                    -HeadHeight() / 2,
                ),
                (
                    NeckBase() + Sliver - CornerSaver + EarWidth(),
                    -HeadHeight() / 2,
                ),
            ),
            (
                (
                    NeckBase() + Sliver + CornerSaver,
                    HeadHeight() / 2,
                ),
                (
                    NeckBase() + Sliver - CornerSaver + EarWidth(),
                    HeadHeight() / 2,
                ),
            ),
            # nose
            (
                (
                    NeckBase() + 2 * Sliver + EarWidth() + FlapThickness,
                    (NoseWidth / 2 - CornerSaver),
                ),
                (
                    NeckBase() + 2 * Sliver + EarWidth() + FlapThickness,
                    -(NoseWidth / 2 - CornerSaver),
                ),
            ),
            (
                (
                    NeckBase() + 2 * Sliver + EarWidth() + 2 * FlapThickness,
                    (NoseWidth / 2 - CornerSaver),
                ),
                (
                    NeckBase() + 2 * Sliver + EarWidth() + 2 * FlapThickness,
                    -(NoseWidth / 2 - CornerSaver),
                ),
            ),
        ]

        if 0 < HeadWidth() - NoseWidth - 2 * CornerSaver:
            foldList.extend(
                [
                    # Face flap
                    (
                        (
                            NeckBase() + HeadWidth(),
                            (HeadHeight() / 2 - CornerSaver),
                        ),
                        (
                            NeckBase() + HeadWidth(),
                            (NoseWidth / 2 + CornerSaver),
                        ),
                    ),
                    (
                        (
                            NeckBase() + HeadWidth(),
                            -(NoseWidth / 2 + CornerSaver),
                        ),
                        (
                            NeckBase() + HeadWidth(),
                            -(HeadHeight() / 2 - CornerSaver),
                        ),
                    ),
                ]
            )

        for fl in foldList:
            foldLine = draw.Path(
                # stroke=randColor(),
                stroke="red",
                stroke_width=2,
            )
            foldLine.M(*fl[0]).L(*fl[1])
            # drawing.append(foldLine)
            for d in dasher(
                *fl,
                args.max_dash_length * inch,
                args.dash_period * inch,
            ):
                drawing.append(d)

    def cutInnerlines():
        cutList = [
            (
                (
                    NeckBase() + HeadWidth(),
                    (NoseWidth / 2),
                ),
                (
                    NeckBase() + HeadWidth(),
                    -(NoseWidth / 2),
                ),
            )
        ]

        for cl in cutList:
            foldLine = draw.Path(
                # stroke=randColor(),
                stroke="blue",
                stroke_width=2,
            )
            foldLine.M(*cl[0]).L(*cl[1])
            drawing.append(foldLine)

    # guideGrid()
    cutOuterLine()
    foldLines()
    cutInnerlines()

    # drawing.append(
    #     draw.Circle(
    #         *DiagonalTopLeft(),
    #         0.1 * inch,
    #         **randFillAttrs(),
    #     )
    # )
    # drawing.append(
    #     draw.Circle(
    #         *DiagonalBottomRight(),
    #         0.1 * inch,
    #         **randFillAttrs(),
    #     )
    # )

    drawing.set_pixel_scale(0.75)
    drawing.save_svg("example.svg")
    drawing.save_png("example.png")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
