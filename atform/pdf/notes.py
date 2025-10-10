"""Generates the Notes section."""

from reportlab.platypus import Flowable, Spacer

from . import (
    layout,
    section,
)


def make_notes() -> Flowable:
    """Creates the Notes section flowable."""
    rows = [[Spacer(0, layout.NOTES_AREA_SIZE)]]
    return section.make_section("Notes", data=rows)
