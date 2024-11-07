# This module implements storage of IDs, such as a test number, referenced by
# a user-provided label.


import re
import string

from . import error
from . import state


# Regular expression pattern to match a valid label, which is based on
# allowable identifiers for template strings.
valid_label_pattern = re.compile(r"\w+$")


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

    if not valid_label_pattern.match(label):
        raise error.UserScriptError(
            f"Invalid label: {label}",
            "Labels may contain only letters, numbers, and underscore."
        )

    # Labels unavailable to be defined in the target mapping because they
    # have already been defined.
    used = set(state.labels)

    # If adding to the global mapping, the used labels include every
    # local scope to prevent adding a global label which would conflict
    # with a previously-defined local label.
    if mapping is None:
        mapping = state.labels
        used.update(state.all_local_labels)

    # If adding to a local mapping, the used labels are a combination of
    # the local mapping and global labels.
    else:
        used.update(mapping)

    if label in used:
        raise error.UserScriptError(
            f"Duplicate label: {label}",
            "Select a label that has not yet been used.",
        )

    state.all_local_labels.add(label)
    mapping[label] = id_


def resolve(orig, mapping):
    """Replaces label placeholders with the target IDs.

    The public API already validates the original string to ensure it is
    in fact a string, so only substitution needs to be checked.
    """
    tpl = string.Template(orig)

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
