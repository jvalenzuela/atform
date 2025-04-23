"""Label storage and replacement.

This module implements storing identifiers, such as a test numbers or
procedure step, referenced by a user-provided label. Labels found within
strings are then replaced with their assigned identifier.
"""

import re
import string

from . import error
from . import state


# Regular expression pattern to match a valid label, which is based on
# allowable identifiers for template strings.
valid_label_pattern = re.compile(r"(?ai:[_a-z][_a-z0-9]*)$")


def add(label, id_, mapping=None):
    """Assigns an identifier to a label.

    This function is not exposed in the public API, however, the label
    argument is passed directly from public API arguments, so it is
    validated here. The id is generated internally by atform, e.g., a test
    number, and can be assumed appropriate.
    """
    if not isinstance(label, str):
        raise error.UserScriptError(
            f"Invalid label data type: {label}",
            "Label must be a string.",
        )

    # The strip() inequality catches trailing newlines permitted by the
    # pattern's "$" suffix.
    if not valid_label_pattern.match(label) or (label != label.strip()):
        raise error.UserScriptError(
            f"Invalid label: {label}",
            """
            Labels must begin with a letter or underscore, optionally
            followed by additional letters, numbers, or underscore.
            """,
        )

    # Default to global labels if a target mapping is omitted.
    if mapping is None:
        mapping = state.labels

    try:
        mapping[label]
    except KeyError:
        mapping[label] = id_
    else:
        raise error.UserScriptError(
            f"Duplicate label: {label}",
            "Select a label that has not yet been used.",
        )


def resolve(orig, mapping, used_labels):
    """Replaces label placeholders with the target text.

    The public API already validates the original string to ensure it is
    in fact a string, so only substitution needs to be checked.
    """
    tpl = string.Template(orig)

    # Add any labels found in the original string. This is not implemented
    # using the get_identifiers() template method to support Python versions
    # older than v3.11.
    used = [lbl for lbl in mapping if tpl.safe_substitute({lbl: ""}) != orig]
    used_labels.update(used)

    try:
        return tpl.substitute(mapping)

    except KeyError as e:
        raise error.UserScriptError(
            f"Undefined label: {e}",
            "Select a label that has been defined.",
        ) from e
    except ValueError as e:
        raise error.UserScriptError(
            "Invalid label replacement syntax.",
            "Labels are formatted as $<name>, where <name> begins with a "
            "letter or underscore, followed by zero or more letters, "
            "numbers, or underscore.",
        ) from e
