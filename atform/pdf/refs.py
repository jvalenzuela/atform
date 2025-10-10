"""References section generation."""

from typing import Optional

from reportlab.platypus import Flowable, Paragraph

from ..addtest import Reference
from . import (
    layout,
    section,
)
from .textstyle import stylesheet


def make_references(refs: list[Reference]) -> Optional[Flowable]:
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


def make_row(ref: Reference) -> list[Flowable]:
    """Creates the table for a single reference category."""
    return [
        Paragraph(ref.title, stylesheet["NormalRight"]),
        Paragraph(", ".join(ref.items), stylesheet["Normal"]),
    ]


def calc_widths(titles: list[str]) -> list[Optional[float]]:
    """Computes table column widths."""
    widths = [
        # First column is sized to fit the longest category title plus
        # LEFTPADDING and RIGHTPADDING.
        (
            layout.max_width(titles, "NormalRight")
            + (2 * layout.DEFAULT_TABLE_HORIZ_PAD)
        ),
        # Second column gets all remaining space.
        None,
    ]

    return widths
