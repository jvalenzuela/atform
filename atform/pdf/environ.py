"""Generates the Environment section."""

from reportlab.platypus import Paragraph

from . import (
    acroform,
    layout,
    section,
)
from .textstyle import stylesheet


def make_environment(fields):
    """Generates the Environment section."""
    if not fields:
        return None

    rows = [create_row(f) for f in fields]

    style = [
        # Horiziontal rule between each item.
        (
            "LINEABOVE",
            (0, 2),
            (-1, -1),
            layout.SUBSECTION_RULE_WEIGHT,
            layout.RULE_COLOR,
        ),
    ]

    return section.make_section(
        "Environment",
        data=rows,
        style=style,
        colWidths=calc_widths(fields),
    )


def create_row(field):
    """Creates a table row for a single field."""
    return [
        Paragraph(field.title, stylesheet["NormalRight"]),
        acroform.TextEntry(field.length),
    ]


def calc_widths(fields):
    """Calculates table column widths."""
    return [
        # Field title widths for column 0.
        layout.max_width(
            [f.title for f in fields],
            "NormalRight",
        ),
        # All remaining width to the text entry column.
        None,
    ]
