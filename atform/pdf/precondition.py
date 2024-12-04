"""Generates the Preconditions section."""

from . import section


def make_preconditions(items):
    """Generates Preconditions section."""
    if not items:
        return None

    return section.make_bullet_list("Preconditions", items)
