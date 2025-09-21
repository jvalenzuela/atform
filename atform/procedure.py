"""This module implements procedure list validation and storage."""

import collections
import dataclasses
import typing

from . import (
    error,
    image,
    label,
    misc,
)


# Container to hold normalized procedure step field definitions. This is
# not part of the public API as fields are defined via normal tuples, which
# are then validated to create instances of this named tuple.
Field = collections.namedtuple(
    "Field",
    ["title", "length", "suffix"],
)


# Largest allowable procedure step image size, in inches. The width is
# selected to fit within the allowable horizontal space allotted to the
# procedure table's Description column; the height chosen arbitrarily.
MAX_IMAGE_SIZE = image.ImageSize(5, 3)


@dataclasses.dataclass(
    repr=False,
    order=False,
)
class Step:
    """Storage for a single procedure step.

    The step validation process converts the user-provided string or dictionary
    into an instance of this class.
    """

    text: str
    fields: typing.List[Field]
    image_hash: bytes

    def resolve_labels(self, mapping):
        """Replaces label placeholders with their target IDs."""
        self.text = label.resolve(self.text, mapping)


def validate(lst, label_mapping):
    """Validates a user-provided list containing procedure steps."""
    if lst is None:
        lst = []
    elif not isinstance(lst, list):
        raise error.UserScriptError("Procedure must be a list.")
    steps = []
    for i, step in enumerate(lst, start=1):
        try:
            steps.append(make_step(step, i, label_mapping))
        except error.UserScriptError as e:
            e.add_field("Procedure Step", i)
            raise
    return steps


def make_step(raw, num, label_mapping):
    """Validates a single procedure step."""
    data = normalize_type(raw)
    step = Step(
        text=validate_text(data),
        fields=validate_fields(data),
        image_hash=validate_image(data),
    )
    validate_label(data, num, label_mapping)
    check_undefined_keys(data)
    return step


def normalize_type(raw):
    """Normalizes the raw data into a dict."""
    # Convert a string to a dict with text key.
    if isinstance(raw, str):
        normalized = {"text": raw}

    elif isinstance(raw, dict):
        # Keys are removed during the validation process so a shallow copy is
        # made to ensure the original argument remains unchanged.
        normalized = dict(raw)

    else:
        raise error.UserScriptError(
            f"Invalid procedure step data type: {type(raw).__name__}",
            "A procedure step must be a string or dictionary.",
        )

    return normalized


def validate_text(data):
    """Validates the text key."""
    try:
        text = data.pop("text")
    except KeyError as e:
        raise error.UserScriptError(
            'A procedure step dictionary must have a "text" key.',
            """
            Add a "text" key with a string value containing instructions
            for the step.
            """,
        ) from e
    return misc.nonempty_string("Procedure step text", text)


def validate_fields(data):
    """Validates the fields key."""
    tpls = data.pop("fields", [])
    if not isinstance(tpls, list):
        raise error.UserScriptError(
            f"Invalid procedure step fields data type: {type(tpls).__name__}",
            "Procedure step fields must be a list.",
        )

    fields = []
    for i, tpl in enumerate(tpls, start=1):
        try:
            fields.append(create_field(tpl))
        except error.UserScriptError as e:
            e.add_field("Procedure Step Field #", i)
            raise
    return fields


def create_field(tpl):
    """Converts a raw procedure step field definition tuple into a named tuple."""
    if not isinstance(tpl, tuple):
        raise error.UserScriptError(
            f"""
            Invalid procedure step field list item data type: {type(tpl).__name__}
            """,
            "Each item in the list of fields for a procedure step must be a tuple.",
        )

    # Validate the required items: title and length.
    try:
        raw_title = tpl[0]
        raw_length = tpl[1]
    except IndexError as e:
        raise error.UserScriptError(
            "Procedure step field tuple is too short.",
            """
            A tuple defining a data entry field for a procedure step must have at
            least two members: title and length.
            """,
        ) from e

    title = misc.nonempty_string("Procedure step field title", raw_title)
    length = misc.validate_field_length(raw_length)

    # Validate suffix, providing a default value if omitted.
    try:
        raw = tpl[2]
    except IndexError:
        suffix = ""
    else:
        suffix = misc.nonempty_string("Procedure step field suffix", raw)

    if len(tpl) > len(Field._fields):
        raise error.UserScriptError(
            "Procedure step field tuple is too long.",
            """
            A tuple defining a data entry field for a procedure step may not exceed
            three members: title, length, and suffix.
            """,
        )

    return Field(title, length, suffix)


def validate_image(data):
    """Loads the file referenced by the image key."""
    try:
        path = data.pop("image")

    # Image is optional, do nothing if omitted.
    except KeyError:
        return None

    return image.load(path, MAX_IMAGE_SIZE)


def validate_label(data, num, mapping):
    """Creates a label referencing the step."""
    try:
        lbl = data.pop("label")

    # Label is optional; do nothing if omitted.
    except KeyError:
        pass

    else:
        label.add(lbl, str(num), mapping)


def check_undefined_keys(data):
    """Checks for undefined keys in a user-provided step dictionary.

    Defined keys are removed from the original dictionary as they are validated, so
    any remaining keys are assumed to be undefined.
    """
    if data:
        keys = ", ".join(str(k) for k in data.keys())
        raise error.UserScriptError(
            f"Undefined procedure step dictionary key(s): {keys}",
        )
