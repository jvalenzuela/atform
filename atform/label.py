# This module implements storage of IDs, such as a test number, referenced by
# a user-provided label.


from . import error
import re
import string


# Target ids keyed by label.
labels = {}


# Regular expression pattern to match a valid label, which is based on
# allowable identifiers for template strings.
valid_label_pattern = re.compile(r"\w+$")


def add(label, id):
    """Assigns an identifier to a label.

    This function is not exposed in the public API, however, the label
    argument is passed directly from public API arguments, so it is
    validated here. The id is generated internally by atform, e.g., a test
    number, and can be assumed appropriate.
    """
    global labels

    if not isinstance(label, str):
        raise error.UserScriptError('Label must be a string.')

    if not valid_label_pattern.match(label):
        raise error.UserScriptError(
            f"Invalid label: {label}",
            f"Labels may contain only letters, numbers, and underscore."
        )

    if label in labels:
        raise error.UserScriptError(
            f"Duplicate label: {label}",
            "Select a label that has not yet been used.",
        )

    labels[label] = id


def resolve(orig):
    """Replaces label placeholders with the target IDs.

    The public API already validates the original string to ensure it is
    in fact a string, so only substitution needs to be checked.
    """
    tpl = string.Template(orig)

    try:
        return tpl.substitute(labels)

    except KeyError as e:
        raise error.UserScriptError(
            f"Undefined label: {e}",
            "Select a label that has been defined.",
        )
    except ValueError as e:
        raise error.UserScriptError(
            f"Invalid label replacement syntax.",
            "Labels are formatted as $<name>, where <name> begins with a "
            "letter or underscore, followed by zero or more letters, "
            "numbers, or underscore.",
        )
