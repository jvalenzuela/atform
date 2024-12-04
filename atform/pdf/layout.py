"""Global formatting constants and utilities."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import toLength
from reportlab.pdfbase.pdfmetrics import stringWidth

from .textstyle import stylesheet


PAGE_SIZE = LETTER
LEFT_MARGIN = toLength("0.75 in")
RIGHT_MARGIN = LEFT_MARGIN
TOP_MARGIN = toLength("0.75 in")


# This initial value is based on the single-line footer containing the
# page number and possibly version ID; it will be increased to accommodate
# a user-provided copyright notice.
BOTTOM_MARGIN = toLength("0.5 in")


# Horizontal space available for body content.
BODY_WIDTH = PAGE_SIZE[0] - LEFT_MARGIN - RIGHT_MARGIN


# Default left and right padding for table cells, i.e., default value for
# LEFTPADDING and RIGHTPADDING table style commands.
DEFAULT_TABLE_HORIZ_PAD = toLength("6 pt")


# Thickness of lines separating top-level sections and divisions within
# each section.
SECTION_RULE_WEIGHT = toLength("1 pt")
SUBSECTION_RULE_WEIGHT = toLength("0.5 pt")


# Color for all rules(lines).
RULE_COLOR = colors.black


# Background color for table cells containing top-level section headings.
SECTION_BACKGROUND = colors.lightsteelblue


# Background color for table cells representing divisions within a section.
SUBSECTION_BACKGROUND = colors.lightgrey


# Vertical space between each top-level section.
SECTION_SEP = toLength("5 pt")


# Vertical space allotted for the Notes section.
NOTES_AREA_SIZE = toLength("2 in")


# Text color for the draft watermark.
DRAFTMARK_COLOR = colors.Color(0, 0, 0, 0.3)


def max_width(
    items,
    style_name,
    left_pad=DEFAULT_TABLE_HORIZ_PAD,
    right_pad=DEFAULT_TABLE_HORIZ_PAD,
):
    """Finds the width required to hold the longest among a set of strings.

    Used to size a table column such that it can hold the content
    of all rows in that column.
    """
    style = stylesheet[style_name]
    widths = [stringWidth(i, style.fontName, style.fontSize) for i in items]

    # The final width includes left and right table padding.
    return max(widths) + left_pad + right_pad
