"""Generates the Equipment section."""

from . import section


def make_equipment(equip):
    """Generates the Required Equipment section flowable."""
    if not equip:
        return None

    return section.make_bullet_list("Required Equipment", equip)
