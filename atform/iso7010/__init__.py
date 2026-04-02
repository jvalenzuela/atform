"""This module provides a set of ISO 7010 pictograms in SVG format."""

import functools
from importlib import resources
import sys


# Functional reference numbers, e.g., "M001", of available pictograms.
REFS = frozenset(f.stem for f in resources.files().iterdir() if f.name.endswith(".svg"))


def validate_ref(ref):
    """Verifies a given reference exists."""
    if not isinstance(ref, str):
        raise TypeError
    if not ref in REFS:
        raise KeyError


@functools.cache
def load(ref):
    """Reads the SVG file for a given reference."""
    return resources.read_text(sys.modules[__name__], f"{ref}.svg")
