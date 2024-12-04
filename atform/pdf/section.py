"""Document section generation.

This module contains common utilities for generating top-level document
sections, which are implemented as ReportLab Tables.
"""

from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Preformatted,
    Table,
)

from . import (
    layout,
    paragraph,
)
from .textstyle import stylesheet


# Table style commands applied to all sections.
STYLE = [
    # Border surrounding the entire section.
    ("BOX", (0, 0), (-1, -1), layout.SECTION_RULE_WEIGHT, layout.RULE_COLOR),
    # Title row background.
    ("BACKGROUND", (0, 0), (0, 0), layout.SECTION_BACKGROUND),
    # The title spans all columns.
    ("SPAN", (0, 0), (-1, 0)),
]


def make_section(title, nosplit=True, **kwargs):
    """Creates a table enclosing an entire top-level section."""
    # Add the title as the first row.
    kwargs["data"].insert(0, [Preformatted(title, stylesheet["SectionHeading"])])

    try:
        style = kwargs["style"]
    except KeyError:
        style = []
        kwargs["style"] = style
    style.extend(STYLE)

    # Keep the entire section together unless the table is explicitly built
    # to handle splitting.
    if nosplit:
        style.append(("NOSPLIT", (0, 0), (-1, -1)))

    set_table_width(kwargs)

    return Table(
        spaceAfter=layout.SECTION_SEP,
        **kwargs,
    )


def set_table_width(table_args):
    """Adjusts table column widths to fill all available horizontal space."""
    try:
        widths = table_args["colWidths"]

    # Sections with a single column do not specify widths, so that
    # column occupies the entire width.
    except KeyError:
        table_args["colWidths"] = [layout.BODY_WIDTH]

    # Sections with multiple columns will have one column that will be
    # stretched to occupy all remaining space.
    else:
        stretch_col = widths.index(None)
        remain = layout.BODY_WIDTH - sum(w for w in widths if w)
        widths[stretch_col] = remain


def make_bullet_list(title, items):
    """Creates a section consisting of a simple bullet list.

    The section is built as a table with one item per row;
    each row is comprised of a ListFlowable with a single
    item to create the bullet list formatting.
    """
    rows = [
        [
            ListFlowable(
                # Each item may contain multiple paragraphs, which are
                # expanded to a list of strings.
                [ListItem(paragraph.make_paragraphs(i))],
                bulletType="bullet",
            )
        ]
        for i in items
    ]

    return make_section(title, data=rows)
