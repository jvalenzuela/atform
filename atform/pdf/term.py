"""This module generates the section listing term references."""

from reportlab.lib.units import toLength
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
)

from . import section
from .textstyle import stylesheet


SECTION_TITLE = "Terms"


PREAMBLE = """
The following terms used in this document are further supported in
separate tests, as listed below:
"""


# Vertical space to add between terms.
TERM_SEP = toLength("16 pt")


def make_terms(terms):
    """Generates the top-level section flowable."""
    if not terms:
        return None

    flowables = [Paragraph(PREAMBLE, stylesheet["Normal"])]

    items = []
    for term, tests in terms.items():
        items.extend(term_items(term, tests))
    flowables.append(ListFlowable(items, leftIndent=0))

    return section.make_section(
        SECTION_TITLE,
        data=[[flowables]],
    )


def term_items(term, tests):
    """Creates list items for one term and its supporting tests."""
    style = stylesheet["Normal"]

    # First item is the term itself.
    items = [unnumbered_item(Paragraph(term, style), spaceBefore=TERM_SEP)]

    # Next item is a nested list for supporting tests.
    test_items = [unnumbered_item(Paragraph(t, style)) for t in tests]

    # The nested list is wrapped in a ListItem to prevent it from being
    # numbered in the parent list.
    items.append(unnumbered_item(ListFlowable(test_items)))

    return items


def unnumbered_item(item, **kwargs):
    """Creates an ListFlowable item not preceded by a number."""
    return ListItem(item, value=0, **kwargs)
