"""This module provides a set of ISO 7010 pictograms in SVG format."""

import functools
from importlib import resources
import sys


# Available symbols and their associated meaning. The meanings(values) are
# only used in documentation(Sphinx) and unit tests, residing here as a
# convenient import for both cases.
SYMBOLS = {
    "M001": "General mandatory action sign",
    "M002": "Refer to instruction manual/booklet",
    "M021": "Disconnect before carrying out maintenance or repair",
    "M027": "Check guard",
    "M029": "Sound horn",
    "M068": "Lock moving mechanical parts",
    "M069": "Tools must be tethered",
    "W001": "General warning sign",
    "W002": "Explosive substances",
    "W004": "Laser beam",
    "W006": "Magnetic field",
    "W010": "Low temperature/freezing conditions",
    "W012": "Electricity",
    "W017": "Hot surface",
    "W018": "Automatic start-up",
    "W019": "Crushing",
    "W021": "Flammable material",
    "W024": "Crushing of hands",
    "W026": "Battery charging",
    "W027": "Optical radiation",
    "W037": "Run over by remote operator controlled machine",
    "W038": "Sudden loud noise",
    "W042": "Arc flash",
    "W079": "Hot content",
    "W080": "Hot steam",
    "W087": "High sound volume levels",
    "W089": "Moving gears",
}


def validate(ref):
    """Verifies a given reference exists."""
    if not isinstance(ref, str):
        raise TypeError
    if not ref in SYMBOLS:
        raise KeyError


@functools.cache
def load(ref):
    """Reads the SVG file for a given reference.

    SVG content is loaded as bytes instead of a string because svglib,
    which is used later to process the image, does not support strings
    containing an XML encoding declaration.
    """
    return resources.read_binary(sys.modules[__name__], f"{ref}.svg")
