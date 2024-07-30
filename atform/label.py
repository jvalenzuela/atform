# This module implements storage of IDs, such as a test number, referenced by
# a user-provided label.


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
    label argument is passed directly from public API arguments, so it is
    validated here. The id is generated internally by atform, e.g., a test
    number, and can be assumed appropriate.
    """
    global labels

    if not isinstance(label, str):
        raise TypeError('Label must be a string.')

    if not valid_label_pattern.match(label):
        raise ValueError(
            'Invalid label; only letters, numbers, and underscore are allowed.')

    if label in labels:
        raise ValueError("Duplicate label: {0}".format(label))

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
        raise KeyError("Undefined label: {0}".format(e))
    except ValueError:
        raise ValueError(
            'Invalid label replacement syntax: "{0}"'.format(orig))
