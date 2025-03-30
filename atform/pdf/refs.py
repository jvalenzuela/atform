"""References section generation."""

from reportlab.platypus import Paragraph

from . import (
    layout,
    section,
)
from .textstyle import stylesheet


def make_references(refs):
    """Generates the References section."""
    if not refs:
        return None

    # Generate a row for each reference category.
    rows = [make_row(ref) for ref in refs]

    titles = [ref.title for ref in refs]

    style = [
        (
            "INNERGRID",
            (0, 1),
            (-1, -1),
            layout.SUBSECTION_RULE_WEIGHT,
            layout.RULE_COLOR,
        ),
        # Category column vertical alignment.
        ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
    ]

    return section.make_section(
        "References",
        data=rows,
        style=style,
        colWidths=calc_widths(titles),
    )


def make_row(ref):
    """Creates the table for a single reference category."""
    return [
        Paragraph(ref.title, stylesheet["NormalRight"]),
        Paragraph(", ".join(ref.items), stylesheet["Normal"]),
    ]


def calc_widths(titles):
    """Computes table column widths."""
    widths = [
        # First column is sized to fit the longest category title.
        layout.max_width(titles, "NormalRight"),
        # Second column gets all remaining space.
        None,
    ]

    # Include LEFTPADDING and RIGHTPADDING.
    widths[0] = widths[0] + (2 * layout.DEFAULT_TABLE_HORIZ_PAD)

    return widths
