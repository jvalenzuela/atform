"""Builds the section listing supporting term references."""

from reportlab.lib.units import toLength
from reportlab.platypus import Paragraph

from .. import id as id_
from . import layout
from . import section
from .textstyle import stylesheet


# Maximum horizontal size of the term text column, which is allowed
# to consume most of the available width because the term text may be
# lengthy while the number of supporting tests is typically small.
MAX_COL_WIDTH = layout.BODY_WIDTH * 0.75


def make_terms(terms):
    """Creates a section listing terms and their supporting tests."""
    if not terms:
        return None

    rows = [
        # Static description text in the first row.
        [
            Paragraph(
                """
                The following terms appearing in this procedure are
                supported by additional tests:
                """,
                stylesheet["Normal"],
            )
        ]
    ]

    # Add a row for each term.
    term_rows = [make_term_row(t) for t in terms]
    rows.extend(term_rows)

    style = [
        # Row containing the description spans the entire table.
        ("SPAN", (0, 1), (-1, 1)),
        # Grid lines for term rows.
        (
            "GRID",
            (0, 2),
            (-1, -1),
            layout.SUBSECTION_RULE_WEIGHT,
            layout.RULE_COLOR,
        ),
    ]

    return section.make_section(
        "Supporting Tests",
        data=rows,
        style=style,
        colWidths=calc_widths(term_rows),
    )


def make_term_row(term):
    """Creates a table row for a single term reference."""
    supporting_ids = [id_.to_string(id) for id in sorted(term.test_ids)]
    return [
        Paragraph(term.text, stylesheet["NormalRight"]),
        Paragraph(", ".join(supporting_ids), stylesheet["Normal"]),
    ]


def calc_widths(term_rows):
    """Computes the column widths."""
    # Compute the width required to present the longest term without line
    # wrapping. This uses the Paragraph minWidth() method because the term
    # text may include formatting XML.
    max_term = max(t[0].minWidth() for t in term_rows)

    # Limit the term column width.
    if max_term > MAX_COL_WIDTH:
        term_width = MAX_COL_WIDTH

    # Set the term column width to fit the longest term if all terms fit
    # unwrapped within the column size limit.
    else:
        term_width = (
            max_term
            + (layout.DEFAULT_TABLE_HORIZ_PAD * 2)  # Include table padding.
            + toLength("0.1 pt")  # Tiny additional space to avoid line wrap.
        )

    return [term_width, None]
