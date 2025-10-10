"""Generates the Equipment section."""

from typing import Optional

from reportlab.platypus import Flowable

from . import section


def make_equipment(equip: list[str]) -> Optional[Flowable]:
    """Generates the Required Equipment section flowable."""
    if not equip:
        return None

    return section.make_bullet_list("Required Equipment", equip)
