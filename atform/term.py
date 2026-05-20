"""This module houses the API for handling user-defined terms."""

import collections
import re

from . import error
from . import format as format_
from . import label as label_
from . import misc


Term = collections.namedtuple("Term", ["raw", "formatted"])


# All defined terms, keyed by label.
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
terms = {}


# The set of test IDs, keyed by term label, supporting a given term as
# defined by the supports_term argument to add_test().
#
# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
supporting_tests = {}


def normalize_whitespace(text):
    """Converts consecutive whitespace into a single space."""
    return re.sub(r"\s+", " ", text)


def verify_unique(text):
    """Confirms a term is not already defined."""
    for lbl, term in terms.items():
        if text == term.raw:
            raise error.UserScriptError(
                f"Duplicate term text: {text}",
                remedy=f"""
                This term has already been assigned to the label "{lbl}";
                terms must be unique.
                """,
            )


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_term(text, label, *, typeface="normal", font="normal"):
    """Defines a new term.

    The term can be inserted into test content via its assigned label,
    optionally formatted, and cross-referenced by use.

    .. seealso:: :ref:`term`

    Args:
        text (str): The literal text, typically a word or phrase such as a
            variable name, to be inserted into content wherever the label
            appears. Must be unique among all other terms and not blank.
        label (str): The identifier to be used in test content where this
            term shall appear. See :ref:`labels` for details.
        typeface (str, optional): Typeface to apply to the term text;
            same as :py:func:`atform.format_text`.
        font (str, optional): Font to apply to the term text; same as
            :py:func:`atform.format_text`.
    """
    text = misc.nonempty_string("text", text)
    text = normalize_whitespace(text)
    verify_unique(text)
    format_.validate_typeface(typeface)
    format_.validate_font(font)

    if (typeface == "normal") and (font == "normal"):
        formatted = text
    else:
        formatted = format_.format_text(text, typeface=typeface, font=font)

    label_.add(label, formatted)
    supporting_tests[label] = set()
    terms[label] = Term(text, formatted)
