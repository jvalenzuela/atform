"""User-defined data entry fields.

This module implements the API to create data entry fields and select
which tests they appear on.
"""

import collections
from typing import Optional

from . import error
from . import misc
from . import state


# Object used to store the definition of each field.
Field = collections.namedtuple(
    "Field",
    ["title", "length"],
)


# Type alias for lists of field names given to the API, which default to None.
FieldListType = Optional[list[str]]


def validate_name_list(title: str, lst: FieldListType) -> set[str]:
    """Verifies a list to confirm it contains only valid field names."""
    if lst is None:
        lst = []
    elif not isinstance(lst, list):
        raise error.UserScriptError(
            f"Invalid {title} data type: {type(lst).__name__}",
            f"{title} must be a list of field names.",
        )
    names = set()
    for raw in lst:
        name = misc.nonempty_string("field name", raw)
        try:
            state.fields[name]
        except KeyError as e:
            raise error.UserScriptError(
                f"Undefined name in {title} list: {name}",
                "Use a name defined with atform.add_field().",
            ) from e
        names.add(name)
    return names


def get_active_names(
    include: FieldListType, exclude: FieldListType, active: FieldListType
) -> set[str]:
    """Computes the resulting active names after applying filters."""
    incl = validate_name_list("include fields", include)
    excl = validate_name_list("exclude fields", exclude)
    if active is not None:
        return validate_name_list("active fields", active)
    return state.active_fields.union(incl).difference(excl)


def get_active_fields(
    include: FieldListType, exclude: FieldListType, active: FieldListType
) -> list[Field]:
    """
    Generates the list of field tuples to be applied to the next test
    after applying filters.
    """
    names = list(get_active_names(include, exclude, active))

    # Sort according to order defined by add_field().
    names.sort(key=lambda n: list(state.fields.keys()).index(n))

    return [state.fields[name] for name in names]


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_field(title: str, length: int, name: str, *, active: bool = True) -> None:
    """Adds a user entry field to capture test execution information.

    Form fields are suitable for entering a single line of text at the beginning
    of each test; fields will be listed in the order they were added.
    This function can only be used in the setup area of the script,
    before any tests or sections are created.

    .. seealso:: :ref:`env_fields`

    Args:
        title (str): Text to serve as the field's prompt; must not be blank.
        length (int): Maximum number of characters the field should be sized
            to accommodate; must be greater than zero.
        name (str): A tag used to identify this field; must be unique across
            names given to other fields and not blank.
        active (bool, optional): Set to ``False`` if this field should not
            be included in tests until explicitly activated at a later time,
            such as with :py:func:`atform.set_active_fields`.
    """
    field = Field(
        misc.nonempty_string("field title", title),
        misc.validate_field_length(length),
    )

    name = misc.nonempty_string("field name", name)
    try:
        state.fields[name]
    except KeyError:
        state.fields[name] = field
    else:
        raise error.UserScriptError(
            f"Duplicate field name: {name}",
            "Select a unique field name.",
        )

    if not isinstance(active, bool):
        raise error.UserScriptError(
            f"Invalid active selection: {active}",
            "Set active to False, or omit the argument.",
        )

    if active:
        state.active_fields.add(name)


@error.exit_on_script_error
def set_active_fields(
    *,
    include: FieldListType = None,
    exclude: FieldListType = None,
    active: FieldListType = None,
) -> None:
    """Alters the fields applied to each test created after this function.

    May be called repeatedly to modify the fields applied to different
    tests. The fields set by this function can also be overridden by
    the ``include_fields``, ``exclude_fields``, and ``active_fields``
    arguments of :py:class:`atform.Test`.

    .. seealso:: :ref:`env_fields`

    Args:
        include (list[str], optional): Names of fields to add to later
            tests.
        exclude (list[str], optional): Names of fields to remove from
            later tests.
        active (list[str], optional): If provided, only fields in this
            list will appear in later tests.
    """
    state.active_fields = get_active_names(include, exclude, active)
