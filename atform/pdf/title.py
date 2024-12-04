"""Title block generation.

This module creates the title block at the top of the first page.
"""

from reportlab.lib.units import toLength
from reportlab.platypus import (
    Paragraph,
    Table,
)

from .. import id as id_
from . import layout
from .. import (
    image,
    state,
)
from .textstyle import stylesheet


def make_title(test):
    """
    Creates title information on the top of the first page containing
    project information, test number & title, and logo. Constructed
    as a table with one row; the logo, if any, is the first column,
    and a nested table for the information fields occupies the
    second column.
    """
    rows = [
        [
            state.logo,
            make_fields(test),
        ]
    ]

    style = [
        # Center the logo.
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        # Both the logo and fields table are vertically centered.
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        # Remove right padding from the fields table as it goes all
        # the way to the right margin.
        ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
    ]

    # Remove the left padding from the column containing the fields table
    # if no logo is present, allowing the fields table to abut the
    # left margin.
    if not state.logo:
        style.append(("LEFTPADDING", (1, 0), (1, 0), 0))

    # The image width is fixed to the maximum allowable logo size
    # regardless of the actual image size. If no logo is being used,
    # the image column width is set to zero.
    image_width = toLength(f"{image.MAX_LOGO_SIZE.width} in") if state.logo else 0

    widths = [
        image_width,
        # The fields table occupies all remaining horizontal space.
        layout.BODY_WIDTH - image_width,
    ]

    return Table(
        rows,
        style=style,
        colWidths=widths,
    )


def make_fields(test):
    """Builds a table containing the title block fields."""
    items = []

    # Add optional project information fields.
    try:
        items.append(("Project", test.project_info["project"]))
    except KeyError:
        pass
    try:
        items.append(("System", test.project_info["system"]))
    except KeyError:
        pass

    # Add test identification fields.
    items.append(("Number", id_.to_string(test.id)))
    items.append(("Title", test.title))

    # Add a colon after each field name.
    items = [(f"{i[0]}:", i[1]) for i in items]

    rows = [
        [
            Paragraph(title, stylesheet["HeaderRight"]),
            Paragraph(value, stylesheet["Header"]),
        ]
        for title, value in items
    ]

    style = [
        # Remove horizontal padding from the field name column.
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 0),
        # Vertically align titles with the first line of each field.
        ("VALIGN", (0, 0), (0, -1), "TOP"),
    ]

    widths = [
        layout.max_width(
            [i[0] for i in items],
            "HeaderRight",
            left_pad=0,
            right_pad=0,
        ),
        # The value column is left unspecified as the parent title block
        # table will be stretched to fill.
        None,
    ]

    return Table(
        rows,
        style=style,
        colWidths=widths,
    )
