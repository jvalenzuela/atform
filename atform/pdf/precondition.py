"""Generates the Preconditions section."""

from typing import Optional

from reportlab.platypus import Flowable

from . import section


def make_preconditions(items: list[str]) -> Optional[Flowable]:
    """Generates Preconditions section."""
    if not items:
        return None

    return section.make_bullet_list("Preconditions", items)
