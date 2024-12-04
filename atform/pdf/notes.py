"""Generates the Notes section."""

from reportlab.platypus import Spacer

from . import (
    layout,
    section,
)


def make_notes():
    """Creates the Notes section flowable."""
    rows = [[Spacer(0, layout.NOTES_AREA_SIZE)]]
    return section.make_section("Notes", data=rows)
