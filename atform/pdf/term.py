"""This module generates the section listing term references.

Content in the Terms section is built as a table with one row per item, where
an item is a single term or test. Separating content into individual rows
as opposed as using ListFlowable and ListItem allows the section to span
pages if necessary.
"""

from reportlab.lib.units import toLength
from reportlab.platypus import Paragraph

from . import (
    layout,
    section,
)
from .textstyle import stylesheet


SECTION_TITLE = "Terms"


PREAMBLE = """
The following terms used in this document are further supported in
separate tests, as listed below:
"""


# Vertical space to add between terms.
TERM_SEP = toLength("16 pt")


# Indentation for tests listed under each term; based on the default
# Reportlab ListFlowable left indent.
TEST_INDENT = toLength("18 pt")


def make_terms(terms):
    """Generates the top-level section flowable."""
    if not terms:
        return None

    text_style = stylesheet["Normal"]
    rows = [Paragraph(PREAMBLE, text_style)]
    table_style = [layout.PAGE_BREAK_RULE]

    for term, tests in terms.items():
        first_row = len(rows) + 1  # Offset for the section title.
        table_style.extend(term_style(tests, first_row))

        # Begin with a row listing the term. User-defined formatting is present
        # as in-line markup, so static(normal) text style is applied here
        # as a default.
        rows.append(Paragraph(term, text_style))

        # Add rows listing supporting tests.
        rows.extend(Paragraph(t, text_style) for t in tests)

    return section.make_section(
        SECTION_TITLE,
        data=[[r] for r in rows],
        style=table_style,
        nosplit=False,
    )


def term_style(tests, first_row):
    """Generates table style commands for a single term."""
    term_row = first_row
    first_test_row = term_row + 1
    last_test_row = first_test_row + len(tests) - 1
    return [
        # Vertically separate the term from content above it.
        ("TOPPADDING", (0, term_row), (-1, term_row), TERM_SEP),
        # Indent each test row.
        ("LEFTPADDING", (0, first_test_row), (-1, last_test_row), TEST_INDENT),
    ]
