"""Miscellaneous stuff."""

import functools

from . import error
from . import state


def setup_only(func):
    """
    Decorator for public API functions that can only be called during setup,
    i.e., before any test or sections.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Setup area is determined by the current ID containing all zeros as
        # any new test or section will increment the current ID.
        in_setup = state.current_id.count(0) == len(state.current_id)

        if not in_setup:
            raise error.UserScriptError(
                f"atform.{func.__name__} can only be used in the setup area.",
                "Call this function before any tests or sections are created.",
            )

        return func(*args, **kwargs)

    return wrapper


def nonempty_string(name, s):
    """Checks a string to ensure it is not empty or blank."""
    if not isinstance(s, str):
        raise error.UserScriptError(
            f"Invalid {name} data type: {type(s).__name__}",
            f"{name} must be a string.",
        )
    stripped = s.strip()
    if not stripped:
        raise error.UserScriptError(
            f"{name} cannot be empty.",
            f"Add content to the {name} string, or remove it altogether.",
        )
    return stripped


def validate_field_length(length):
    """Validates a data entry field length."""
    if not isinstance(length, int):
        raise error.UserScriptError(
            f"Invalid field length data type: {type(length).__name__}",
            "Field length must be an integer.",
        )
    if length < 1:
        raise error.UserScriptError(
            f"Invalid field length value: {length}",
            "Field length must be greater than zero.",
        )
    return length


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@setup_only
def add_copyright(notice):
    """Defines a copyright notice that will appear on each test document.

    May only be called once in the setup area.

    .. seealso:: :ref:`setup`

    Args:
        notice (str): The copyright notice text; must be a single
            paragraph and may not be blank.
    """
    if state.copyright_:
        raise error.UserScriptError(
            "A copyright notice has already been defined.",
            """
            This function can only be called once to define a single
            copyright notice.
            """,
        )

    state.copyright_ = nonempty_string("copyright notice", notice)


@error.exit_on_script_error
# Avoid Pylint false-positive as function arguments are accessed via locals().
# pylint: disable=unused-argument
def set_project_info(*, project=None, system=None):
    """Assigns project metadata.

    Information set by this function is used to populate the headers
    and footers. May be used in both setup and content areas.

    .. seealso:: :ref:`project_info`

    Args:
        project (str, optional): Name or description of the project; must
            not be blank.
        system (str, optional): Name or description of the system being tested;
            must not be blank.
    """
    params = locals()
    for arg in params:
        if params[arg] is not None:
            state.project_info[arg] = nonempty_string(arg, params[arg])

# Valid values accepted by set_checkbox_style().
CHECKBOX_STYLES = ("form", "plain")

@error.exit_on_script_error
@setup_only
def set_checkbox_style(style):
    """Selects the appearance of the procedure "Pass" checkbox.

    May only be called once in the setup area.

    Args:
        style (str): ``"form"`` (default) creates an interactive,
            fillable PDF form field for each step. ``"plain"`` draws a
            plain, non-interactive box intended for manual marking.
    """
    if style not in CHECKBOX_STYLES:
        raise error.UserScriptError(
            f"Invalid checkbox style: {style!r}",
            f"""
            Checkbox style must be one of: {", ".join(CHECKBOX_STYLES)}.
            """,
        )
    state.checkbox_style = style

# Valid values accepted by set_signature_style().
SIGNATURE_STYLES = ("form", "plain")

@error.exit_on_script_error
@setup_only
def set_signature_style(style):
    """Selects the appearance of the signature field.

    May only be called once in the setup area.

    Args:
        style (str): ``"form"`` (default) creates an interactive,
            fillable PDF form field for the "name" and "date"  
            elements for each signature. 
            ``"plain"`` draws blank fields for manual entry.
    """
    if style not in SIGNATURE_STYLES:
        raise error.UserScriptError(
            f"Invalid signature style: {style!r}",
            f"""
            Signature style must be one of: {", ".join(SIGNATURE_STYLES)}.
            """,
        )
    state.signature_style = style
