"""Generates embedded notices."""

import io

from reportlab.lib.units import toLength
from reportlab.platypus import Table
import svglib

from .. import iso7010
from . import paragraph


# Horizontal size of the ISO 7010 pictogram. Vertical size is computed
# automatically to maintain the aspect ratio.
IMAGE_WIDTH = toLength("0.5 in")


def to_flowable(notice):
    """Generates a flowable depicting an embedded notice.

    Notices are formatted as a single-row table with the pictogram in the
    first column and the message in the second column.
    """
    row = [
        get_image(notice.symbol),
        paragraph.make_paragraphs(notice.msg, "NoticeMessage"),
    ]
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Remove horizontal padding on either side of the image.
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
    ]
    widths = [IMAGE_WIDTH, None]
    return Table(
        [row],
        style=style,
        colWidths=widths,
    )


def get_image(num):
    """Creates a ReportLab image from a given ISO 7010 number."""
    svg = iso7010.load(num)
    buf = io.BytesIO(svg)
    dwg = svglib.svglib.svg2rlg(buf)
    scale = IMAGE_WIDTH / dwg.width
    dwg.scale(scale, scale)
    dwg.width *= scale
    dwg.height *= scale
    return dwg
