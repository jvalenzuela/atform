"""Creates table content for the approval section.

Each signature is built with two rows; the upper row carries the titles
above each field and the lower row is the actual data entry fields.
"""

import itertools

from reportlab.lib.units import toLength
from reportlab.platypus import (
    Paragraph,
    Preformatted,
)

from . import (
    acroform,
    layout,
    section,
)
from .textstyle import stylesheet

from .. import state

# Number of characters the name text entry fields should be sized to
# accommodate.
NAME_WIDTH = 12


DATE_FORMAT = "YYYY/MM/DD"
DATE_TITLE = f"Date ({DATE_FORMAT})"


# Vertical distance between field names and the data entry fields.
HEADER_SECTION_HEIGHT = toLength("2 pt")

# Set minimum height for name/signature fields depending on table style:
if state.signature_style_plain:
    FIELD_SECTION_HEIGHT = toLength("14 pt")  # Allows space for handwritten field
else:
    FIELD_SECTION_HEIGHT = 0  # no specific height when using acroform


# Column indices.
col_num = 0

NAME_COL = col_num
col_num += 1
SIG_COL = col_num
col_num += 1
INITIAL_COL = col_num
col_num += 1
DATE_COL = col_num


def make_approval(test):
    """Generates the approval section."""
    sigs = test.signatures

    if not sigs:
        return None

    rows = list(itertools.chain.from_iterable([make_sig_rows(title) for title in sigs]))
    widths = [
        name_col_width(),
        None,  # Signature occupies all remaining width.
        # The Initials column is sized to hold the header text.
        layout.max_width(["Initials"], "SignatureFieldTitle"),
        date_col_width(),
    ]
    style = list(
        itertools.chain.from_iterable(
            [sig_row_style(i, sigs) for i, sig in enumerate(sigs)]
        )
    )

    return section.make_section(
        "Approval",
        data=rows,
        colWidths=widths,
        style=style,
    )


def make_sig_rows(title):
    """Generates a set of table rows for a given signature entry.

    Returns form fillable fields or plain fields depending on signature style.
    """
    if state.signature_style_plain:
        return [
            [Paragraph(title, stylesheet["SignatureTitle"])],
            # Middle row has the field titles.
            header_row(),
            # Lower row contains the text entry fields.
            [
                None,  # Name column is blank
                None,  # Signature column is blank.
                None,  # Initial field is blank
                None,  # Date column is blank.
            ],
        ]
    return [
        [Paragraph(title, stylesheet["SignatureTitle"])],
        # Middle row has the field titles.
        header_row(),
        # Lower row contains the text entry fields.
        [
            name_entry_field(),
            None,  # Signature column is blank.
            None,  # Initial field is blank
            date_entry_field(),
        ],
    ]


def header_row():
    """Generates the table row labeling each field."""
    sty = stylesheet["SignatureFieldTitle"]
    return [
        Preformatted("Name", sty),
        Preformatted("Signature", sty),
        Preformatted("Initials", sty),
        Preformatted(DATE_TITLE, sty),
    ]


def name_entry_field():
    """Creates a name entry field."""
    return acroform.TextEntry(NAME_WIDTH)


def date_entry_field():
    """Creates a date entry field."""
    return acroform.TextEntry(DATE_FORMAT, DATE_FORMAT)


def sig_row_style(i, sigs):
    """Generates style commands for the rows of a single signature entry."""
    # Calculate the indices for the rows assigned to this signature.
    title = (i * 3) + 1
    header = title + 1
    field = header + 1

    sty = [
        # Title row spans all columns.
        ("SPAN", (0, title), (-1, title)),
        # Set padding between the headers and fields.
        ("BOTTOMPADDING", (0, header), (-1, header), HEADER_SECTION_HEIGHT),
        ("TOPPADDING", (0, field), (-1, field), FIELD_SECTION_HEIGHT),
        # The name field should abut the left table border.
        (
            "LEFTPADDING",
            (NAME_COL, field),
            (NAME_COL, field),
            layout.SECTION_RULE_WEIGHT / 2,
        ),
        # Remove the left padding from both the date header and field to
        # keep the cell contents off the right tabel border.
        ("LEFTPADDING", (DATE_COL, header), (DATE_COL, field), 0),
    ]

    # Add a horizontal rule below each signature except the last, which
    # is terminated by the enclosing section border.
    last_sig = len(sigs) - 1
    if i != last_sig:
        hrule_weight = layout.SUBSECTION_RULE_WEIGHT
        sty.append(
            (
                "LINEBELOW",
                (0, field),
                (-1, field),
                hrule_weight,
                layout.RULE_COLOR,
            )
        )
    else:
        hrule_weight = layout.SECTION_RULE_WEIGHT

    # Adjust the padding below the fields so they sit on the rule below them.
    sty.append(("BOTTOMPADDING", (0, field), (-1, field), hrule_weight / 2))

    return sty


def name_col_width():
    """Calculates the width of the name column."""
    return name_entry_field().wrap()[0]


def date_col_width():
    """Calculates the width of the date column.

    Includes half the section rule weight because this column abuts the
    right table border.
    """
    return date_entry_field().wrap()[0] + (layout.SECTION_RULE_WEIGHT / 2)
