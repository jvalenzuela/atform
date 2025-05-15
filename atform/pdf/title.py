"""Title block generation.

This module creates the title block at the top of the first page.
"""

from reportlab.platypus import (
    Paragraph,
    Table,
)

from . import layout
from .textstyle import stylesheet


# Table coordinates.
LOGO_COL = 0
LOGO_ROW = 0
LOGO_CELL = (LOGO_COL, LOGO_ROW)
PRJ_INFO_COL = 1
PRJ_INFO_ROW = 0
PRJ_INFO_CELL = (PRJ_INFO_COL, PRJ_INFO_ROW)
TITLE_COL = 1
TITLE_ROW = 1
TITLE_CELL = (TITLE_COL, TITLE_ROW)


# Style for the entire title block table.
TABLE_STYLE = [
    ("SPAN", (LOGO_COL, LOGO_ROW), (LOGO_COL, -1)),
    ("VALIGN", LOGO_CELL, LOGO_CELL, "MIDDLE"),
    # Remove all padding surrounding the logo; padding between the logo
    # and title block text is in the text column.
    ("TOPPADDING", LOGO_CELL, LOGO_CELL, 0),
    ("BOTTOMPADDING", LOGO_CELL, LOGO_CELL, 0),
    ("LEFTPADDING", LOGO_CELL, LOGO_CELL, 0),
    ("RIGHTPADDING", LOGO_CELL, LOGO_CELL, 0),
    ("TOPPADDING", PRJ_INFO_CELL, PRJ_INFO_CELL, 0),
    ("BOTTOMPADDING", PRJ_INFO_CELL, PRJ_INFO_CELL, 0),
    ("VALIGN", PRJ_INFO_CELL, PRJ_INFO_CELL, "TOP"),
    # Remove right padding to align all text with the right margin.
    ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
    ("BOTTOMPADDING", TITLE_CELL, TITLE_CELL, 0),
]


# Style for the child table containing project information.
PRJ_INFO_TABLE_STYLE = [
    # Remove all padding; the parent title block table supplies any
    # necessary padding surrounding this table.
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]


def make_title(test, images):
    """Creates title information on the top of the first page."""
    prj_info = project_info_table(test)

    # Disable the title block if no information was given other than the
    # test title.
    if not prj_info and not test.logo_hash:
        return None

    try:
        logo = images[test.logo_hash]
    except KeyError:
        logo = None

    rows = [
        [logo, prj_info],
        [None, Paragraph(test.full_name, stylesheet["HeaderRight"])],
    ]

    widths = [0, 0]

    if test.logo_hash:
        widths[LOGO_COL] = logo.drawWidth

    # The text column occupies all remaining horizontal space left over
    # from the logo.
    widths[TITLE_COL] = layout.BODY_WIDTH - widths[LOGO_COL]

    return Table(
        rows,
        style=TABLE_STYLE,
        colWidths=widths,
        spaceAfter=layout.SECTION_SEP,
    )


def project_info_table(test):
    """Builds the child table containing project information.

    Project information is contained in a dedicated child table to keep
    the vertical space between rows constant, regardless of the total
    height of the entire title block.
    """
    rows = []

    try:
        project = test.project_info["project"]
    except KeyError:
        pass
    else:
        rows.append(Paragraph(project, stylesheet["ProjectName"]))

    try:
        system = test.project_info["system"]
    except KeyError:
        pass
    else:
        rows.append(Paragraph(system, stylesheet["SystemName"]))

    if rows:
        return Table(
            [[r] for r in rows],
            style=PRJ_INFO_TABLE_STYLE,
        )

    return None
