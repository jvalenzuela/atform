"""Generates the Objective section."""

from . import (
    paragraph,
    section,
)


def make_objective(obj):
    """Creates the Objective section flowable."""
    if not obj:
        return None

    rows = [[paragraph.make_paragraphs(obj)]]
    return section.make_section("Objective", data=rows)
