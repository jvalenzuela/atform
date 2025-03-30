"""Creates table content for the approval section.

Each signature is built with two rows; the upper row carries the titles
above each field and the lower row is the actual data entry fields.
"""

import itertools

from reportlab.lib.units import toLength
from reportlab.pdfbase.pdfmetrics import stringWidth
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


# Number of characters the name text entry fields should be sized to
# accommodate.
NAME_WIDTH = 12


# Vertical distance between field names and the data entry fields.
FIELD_TITLE_SEP = toLength("1 pt")


# Column indices.
TITLE_COL = 0
NAME_COL = TITLE_COL + 1
SIG_COL = NAME_COL + 1
INITIAL_COL = SIG_COL + 1
DATE_COL = INITIAL_COL + 1


def make_approval(test):
    """Generates the approval section."""
    sigs = test.signatures

    if not sigs:
        return None

    rows = list(itertools.chain.from_iterable([make_sig_rows(title) for title in sigs]))
    return section.make_section(
        "Approval",
        data=rows,
        colWidths=widths(sigs),
        style=style(sigs),
    )


def make_sig_rows(title):
    """Generates a row for a given signature entry."""
    field_style = stylesheet["SignatureFieldTitle"]

    return [
        # Top row has the signature and field titles.
        [
            Paragraph(title, stylesheet["NormalRight"]),
            Preformatted("Name", field_style),
            Preformatted("Signature", field_style),
            Preformatted("Initials", field_style),
            Preformatted("Date", field_style),
        ],
        # Lower row contains the text entry fields.
        [
            None,  # Title column in empty in this row.
            name_entry_field(),
            None,  # Signature column is blank.
            None,  # Initial column is blank.
            date_entry_field(),
        ],
    ]


def name_entry_field():
    """Creates a name entry field."""
    return acroform.TextEntry(NAME_WIDTH)


def date_entry_field():
    """Creates a date entry field."""
    return acroform.TextEntry("0000/00/00", "YYYY/MM/DD")


def style(sigs):
    """Generates style commands for the entire table."""
    sty = list(
        itertools.chain.from_iterable(
            [sig_row_style(i, sigs) for i, sig in enumerate(sigs)]
        )
    )

    sty.extend(
        [
            # Vertical rules.
            (
                "LINEBEFORE",
                (NAME_COL, 1),
                (-1, -1),
                layout.SUBSECTION_RULE_WEIGHT,
                layout.RULE_COLOR,
            ),
            # Remove all vertical padding around title column as it
            # spans two rows.
            ("TOPPADDING", (TITLE_COL, 1), (TITLE_COL, -1), 0),
            ("BOTTOMPADDING", (TITLE_COL, 1), (TITLE_COL, -1), 0),
            # Vertically center the title column.
            ("VALIGN", (TITLE_COL, 1), (TITLE_COL, -1), "MIDDLE"),
        ]
    )

    return sty


def sig_row_style(i, sigs):
    """Generates style commands for the two rows of a signature entry."""
    # Calculate the indices for the two rows assigned to this signature.
    upper = (i * 2) + 1
    lower = upper + 1

    sty = [
        # Title column spans both upper and lower rows.
        ("SPAN", (TITLE_COL, upper), (TITLE_COL, lower)),
        # Remove vertical padding above the upper field name row.
        ("TOPPADDING", (NAME_COL, upper), (-1, upper), 0),
        # Set padding between the upper and lower row.
        ("BOTTOMPADDING", (NAME_COL, upper), (-1, upper), FIELD_TITLE_SEP),
        # Remove padding above the entire lower row.
        ("TOPPADDING", (0, lower), (-1, lower), 0),
    ]

    last_row = i + 1 == len(sigs)
    if not last_row:
        # Rule below all but the last row are subsection rules.
        hrule_weight = layout.SUBSECTION_RULE_WEIGHT

        # Horizontal rule beween each signature, except below the last
        # row because it's closed by a section rule.
        sty.append(
            (
                "LINEBELOW",
                (0, lower),
                (-1, lower),
                layout.SUBSECTION_RULE_WEIGHT,
                layout.RULE_COLOR,
            )
        )
    else:
        # Rule below the last row is a section rule.
        hrule_weight = layout.SECTION_RULE_WEIGHT

    # Adjust padding around the data entry fields(name and date).
    for col in [NAME_COL, DATE_COL]:
        # Set left padding so the entry fields abut the subsection rule
        # to the left.
        sty.append(
            (
                "LEFTPADDING",
                (col, lower),
                (col, lower),
                layout.SUBSECTION_RULE_WEIGHT / 2,
            )
        )

        # Set bottom padding so the fields rest on the rule below them.
        sty.append(("BOTTOMPADDING", (col, lower), (col, lower), hrule_weight / 2))

    return sty


def widths(sigs):
    """Computes the column widths of the entire table."""
    return [
        # Width of the first column is set to accommodate the
        # longest title.
        layout.max_width(sigs, "Normal"),
        name_col_width(),
        None,  # Signature occupies all remaining width.
        # The Initials column is sized to hold the title.
        layout.max_width(["Initials"], "SignatureFieldTitle"),
        date_col_width(),
    ]


def name_col_width():
    """Calculates the width of the name column."""
    sty = stylesheet["SignatureFieldTitle"]
    title_width = stringWidth("Name", sty.fontName, sty.fontSize)

    # The title cell includes default left and right padding.
    title_width += layout.DEFAULT_TABLE_HORIZ_PAD * 2

    widest = max(
        [
            title_width,
            name_entry_field().wrap()[0],
        ]
    )

    return widest + layout.SUBSECTION_RULE_WEIGHT


def date_col_width():
    """Calculates the width of the date column."""
    sty = stylesheet["SignatureFieldTitle"]
    title_width = stringWidth("Date", sty.fontName, sty.fontSize)

    # The title cell includes default left and right padding.
    title_width += layout.DEFAULT_TABLE_HORIZ_PAD * 2

    widest = max(
        [
            title_width,
            date_entry_field().wrap()[0],
        ]
    )

    return (
        widest
        + (layout.SUBSECTION_RULE_WEIGHT / 2)  # Left side rule.
        + (layout.SECTION_RULE_WEIGHT / 2)  # Right side rule.
    )
