"""This module handles creating content for the procedure list.

The procedure list is built as a table, with one row per step.
"""

from reportlab.lib.units import toLength
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
)

from . import (
    acroform,
    layout,
    paragraph,
    section,
)
from .textstyle import stylesheet
from .. import state


# Header row text.
HEADER_FIELDS = ["Step #", "Description", "Pass"]


# Column indices.
STEP_COL = 0
DESC_COL = 1
PASS_COL = 2


# Vertical space inserted between step text and the image; inserted only
# when an image is present, and selected to provide sufficient space
# for descenders on the bottom row of text.
IMAGE_SEP = toLength("12 pt")


# Vertical space above the data entry fields.
FIELD_TABLE_SEP = toLength("12 pt")


# Table column indices.
FIELD_TITLE_COL = 0
FIELD_ENTRY_COL = 1
FIELD_SUFFIX_COL = 2


# Style applied to a single-row table containing a single data entry field.
FIELD_TABLE_STYLE = [
    # Remove left padding from the first column to keep the entire
    # set of fields left-aligned with the parent procedure step.
    # Right padding remains to separate the title from the text
    # entry field.
    ("LEFTPADDING", (FIELD_TITLE_COL, 0), (FIELD_TITLE_COL, -1), 0),
    # Remove all horizontal padding surrounding the text entry field.
    # Separation from adjacent columns is provided by padding in
    # those other columns.
    ("LEFTPADDING", (FIELD_ENTRY_COL, 0), (FIELD_ENTRY_COL, -1), 0),
    ("RIGHTPADDING", (FIELD_ENTRY_COL, 0), (FIELD_ENTRY_COL, -1), 0),
]


def make_procedure(steps):
    """Generates the procedure section."""
    if not steps:
        return None

    rows = []
    rows.append(header())
    rows.extend(step_rows(steps))
    rows.append(last_row())

    style = [
        # Header row shading.
        ("BACKGROUND", (0, 1), (-1, 1), layout.SUBSECTION_BACKGROUND),
        # Add a section rule above the header row. This is unnecessary
        # on the initial page, however, it's the only way to get
        # a rule on the top of following pages because the 'splitfirst'
        # index doesn't apply to repeated rows.
        ("LINEABOVE", (0, 1), (-1, 1), layout.SECTION_RULE_WEIGHT, layout.RULE_COLOR),
        # Do not split between the section header row and first step.
        ("NOSPLIT", (0, 0), (-1, 2)),
        # Do not split between the final step and last row.
        ("NOSPLIT", (0, -2), (0, -1)),
        # Horizontal rules between each step.
        (
            "LINEBELOW",
            (0, 2),
            (-1, -3),
            layout.SUBSECTION_RULE_WEIGHT,
            layout.RULE_COLOR,
        ),
        # Step number column
        ("VALIGN", (STEP_COL, 2), (STEP_COL, -2), "MIDDLE"),
        # Checkbox column
        ("ALIGN", (PASS_COL, 2), (PASS_COL, -2), "CENTER"),
        ("VALIGN", (PASS_COL, 2), (PASS_COL, -2), "MIDDLE"),
        # Last row shading.
        ("BACKGROUND", (0, -1), (-1, -1), layout.SUBSECTION_BACKGROUND),
        # Last row spans all columns.
        ("SPAN", (0, -1), (-1, -1)),
        # Add a section rule at the bottom of every page break.
        (
            "LINEBELOW",
            (0, "splitlast"),
            (-1, "splitlast"),
            layout.SECTION_RULE_WEIGHT,
            layout.RULE_COLOR,
        ),
    ]

    return section.make_section(
        "Procedure",
        nosplit=False,
        data=rows,
        style=style,
        colWidths=calc_widths(steps),
        repeatRows=(1,),
    )


def header():
    """Generates the header row."""
    style = stylesheet["ProcedureTableHeading"]
    return [Paragraph(s, style) for s in HEADER_FIELDS]


def step_rows(steps):
    """Creates rows for all steps."""
    step_style = stylesheet["ProcedureTableHeading"]
    return [
        [
            Paragraph(str(i), step_style),
            step_body(step),
            acroform.Checkbox(),
        ]
        for i, step in enumerate(steps, start=1)
    ]


def step_body(step):
    """
    Creates flowables containing all user-defined content for a single
    step, i.e., everything that goes in the Description column.
    """
    # Begin with the step instruction text.
    flowables = paragraph.make_paragraphs(step.text)

    if step.image_hash:
        flowables.append(Spacer(0, IMAGE_SEP))
        flowables.append(state.images[step.image_hash])
    if step.fields:
        flowables.extend(make_fields(step.fields))

    return flowables


def last_row():
    """Creates the final row indicating the end of the procedure."""
    return [Paragraph("End Procedure", stylesheet["ProcedureTableHeading"])]


def calc_widths(steps):
    """Computes column widths for the overall table."""
    style = "ProcedureTableHeading"

    widths = []

    # Width of the step column is set to accommodate the larger of
    # the column header text and the last step number.
    step_col_items = [
        HEADER_FIELDS[STEP_COL],
        str(len(steps)),
    ]
    widths.append(layout.max_width(step_col_items, style))

    # Leave the description column undefined as it will be
    # dynamically sized to consume all remaining width.
    widths.append(None)

    # Pass column width is set to accommodate the larger of the
    # column header and checkboxes.
    pass_col_items = [
        layout.max_width([HEADER_FIELDS[PASS_COL]], style),
        acroform.Checkbox().wrap()[0] + (layout.DEFAULT_TABLE_HORIZ_PAD * 2),
    ]

    # Add a miniscule amount of width to the pass column to avoid
    # wrapping the first header row. It is unknown why this is required
    # and only affects the initial header row while repeated header rows
    # on additional pages do not wrap.
    widths.append(max(pass_col_items) + 0.1)

    return widths


def make_fields(fields):
    """Generates data entry fields for a single procedure step.

    Each field is implemented as a table with one row to permit varying
    column widths among each field.
    """
    # Width of the title column for every field is set to accommodate
    # the longest title.
    title_col_width = layout.max_width(
        [f.title for f in fields],
        "Normal",
        left_pad=0,
    )

    flowables = [Spacer(0, FIELD_TABLE_SEP)]
    flowables.extend([make_field_row(f, title_col_width) for f in fields])
    return flowables


def make_field_row(field, title_col_width):
    """Constructs a single-row table representing a single field."""
    text_entry_field = acroform.TextEntry(field.length)
    row = [
        Paragraph(field.title, stylesheet["NormalRight"]),
        text_entry_field,
    ]

    # Add the optional suffix.
    if field.suffix:
        row.append(Paragraph(field.suffix, stylesheet["Normal"]))

    widths = [
        title_col_width,
        text_entry_field.wrap()[0],
        None,
    ]

    return Table(
        [row],
        colWidths=widths,
        style=FIELD_TABLE_STYLE,
    )
