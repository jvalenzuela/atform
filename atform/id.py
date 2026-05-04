"""Test identifier management.

This module manages the numeric identifiers assigned to each test.
Identifiers are presented in string form as a series of integers
delimited by period, and are internally represented as a tuple
of integers.
"""

import pathlib
import tempfile

from . import error
from . import state


# Type alias for the internal representation of numeric test and section IDs.
IdType = tuple[int, ...]


# This attribute must only be accessed externally by importing the entire
# module; see the state module for details.
section_titles: dict[IdType, str] = {}


def get_id():
    """Returns the identifier to be used for the next test."""
    # Increment last ID level for each test.
    state.current_id[-1] = state.current_id[-1] + 1

    return tuple(state.current_id)


def to_string(id_):
    """Generates a presentation string for a given ID tuple."""
    return ".".join(str(x) for x in id_)


def validate_level(level):
    """Validates a section() level parameter."""
    if not isinstance(level, int):
        raise error.UserScriptError(
            f"Invalid section level data type: {type(level).__name__}",
            "Section level must be an integer.",
        )
    if level < 1:
        raise error.UserScriptError(
            f"Invalid section level: {level}",
            "Use a section level greater than zero.",
        )


def validate_resume(level, id_, title, resume, depth):
    """Validates the section() resume parameter."""
    if not isinstance(resume, bool):
        raise error.UserScriptError(
            f"Invalid resume data type: {type(resume).__name__}",
            "resume must be a boolean.",
        )

    # Any further validations are relevant only when resuming.
    if not resume:
        return

    if id_ is not None:
        raise error.UserScriptError(
            """
            The section ID may not be specified when resuming an
            existing section.
            """,
            """
            Remove the id parameter to resume an existing section,
            or the resume parameter to create a new section.
            """,
        )
    if title is not None:
        raise error.UserScriptError(
            """
            The section title may not be specified when resuming an
            existing section.
            """,
            """
            Remove the title parameter to resume an existing section,
            or the resume paramter to create a new section with that
            title.
            """,
        )
    if level >= depth:
        raise error.UserScriptError(
            f"""
            This call to atform.section() creates a new level {level}
            section, which cannot also resumed here.
            """,
            f"""
            Remove the resume parameter to create a new level {level}
            subsection, or select a section level less than {level} to
            resume there.
            """,
        )


def create_subsection(level, section_id, test_id):
    """Creates a subsection below the current section."""
    # Increment the test ID and make it part of the new section ID,
    # ensuring the new section ID differs from a test created immediately
    # before this call.
    section_id.append(test_id + 1)

    # Add any additional subsection levels beyond the immediate child.
    section_id.extend([1] * (level - len(section_id)))

    return 0  # Test ID is reset in the new subsection.


def increment_section(section_id):
    """Creates a new section at the same level as the current section."""
    section_id[-1] += 1
    return 0  # Test ID is reset in the new section.


def increment_parent_section(level, section_id):
    """Creates a new section in a parent of the current section."""
    del section_id[level:]  # Remove subsections beneath the new level.
    section_id[-1] += 1
    return 0  # Test ID is reset in the new section.


def resume_section(level, section_id):
    """Resumes numbering in a parent section without creating a new section."""
    # The ID value at the target section level becomes the new test ID.
    test_id = section_id[level]

    del section_id[level:]  # Remove subsections beneath the target level.
    return test_id


def skip_section(section_id, id_):
    """Advances the current section level to a given ID."""
    if not isinstance(id_, int):
        raise error.UserScriptError(
            f"Invalid id data type: {type(id).__name__}",
            "id must be an integer.",
        )

    # The current level value is the last number because the section ID has
    # already been sized to the current level.
    current = section_id[-1]

    # Enforce forward jumps.
    if id_ == current:
        raise error.UserScriptError(
            f"Unnecessary id value: {id_}.",
            f"""
            This call to atform.section() automatically advances the
            section to {to_string(section_id)}, making the id unnecessary
            as it is targeting the same section.
            Use an id greater than {current} or remove the
            id parameter.
            """,
        )
    if id_ < current:
        raise error.UserScriptError(
            f"Invalid id value: {id_}.",
            f"""
            The section is currently {to_string(section_id)}, so
            attempting to set the level {len(section_id)} section to {id_}
            is not a forward jump. The id parameter can only be used to
            move forward; use an id greater than {current} or remove the
            id parameter.
            """,
        )

    section_id[-1] = id_


def validate_section_title(title):
    """Confirms a section title is valid.

    Validation is implemented by attempting to create a folder named with
    the title in a temporary directory.
    """
    if not isinstance(title, str):
        raise error.UserScriptError(
            f"Invalid section title data type: {type(title).__name__}",
            "Section title must be a string.",
        )

    with tempfile.TemporaryDirectory() as tdir:
        path = pathlib.Path(tdir, title)
        try:
            path.mkdir()
        except OSError as e:
            raise error.UserScriptError(
                f"Invalid section title: '{title}'",
                """
                Use a section title that is also a valid file system
                folder name.
                """,
            ) from e


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
# Allow id parameter to shadow id() built-in.
# pylint: disable-next=redefined-builtin
def section(level, *, id=None, title=None, resume=False):
    """Creates a new section or subsection.

    The target section level is incremented if ``resume`` is ``False``,
    and the new section can be given an optional title.

    .. seealso:: :ref:`section`

    Args:
        level (int): Target identifier level in which to start a new section;
            must be greater than zero.
        id (int, optional): Target section value; target section is incremented
            by one if omitted. If specified, it must result in a jump
            forward relative to the current section, i.e., jumping backwards,
            or even to the current section, is not permitted.
        title (str, optional): Section title; this information is only used
            to name the folder where output PDFs for tests in
            this section are generated, and consequently may only contain
            characters allowed in file system folder names. If not provided,
            the section folder name will just be the section number.
        resume (bool, optional): Set to ``True`` to continue numbering at
            the target section level without creating a new section.
            The target section level must be less than the current section
            level, i.e., only a parent section can be resumed, and the
            ``id`` and ``title`` parameters cannot be used when resuming.
    """
    validate_level(level)

    # Separate the current ID into the section(everything except the final
    # field) and test(the final field).
    section_id = state.current_id[:-1]
    test_id = state.current_id[-1]

    depth = len(section_id)
    validate_resume(level, id, title, resume, depth)

    # Create a new subsection below the current level.
    if level > depth:
        test_id = create_subsection(level, section_id, test_id)

    # Create a new section at the same level.
    elif level == depth:
        test_id = increment_section(section_id)

    # Create or resume a parent section.
    else:
        if resume:
            test_id = resume_section(level, section_id)
        else:
            test_id = increment_parent_section(level, section_id)

    if id is not None:
        skip_section(section_id, id)

    if title is not None:
        validate_section_title(title)
        stripped = title.strip()
        if stripped:
            section_titles[tuple(section_id)] = stripped

    # Combine the section and test IDs as the new current ID.
    state.current_id = section_id
    state.current_id.append(test_id)


@error.exit_on_script_error
# Allow id parameter to shadow id() built-in.
# pylint: disable-next=redefined-builtin
def skip_test(id=None):
    """Omits one or more tests.

    This function can only skip tests within the current section, i.e.,
    it will only affect the last identifier field. Typical usage is to
    reserve a range of IDs or maintain numbering if a test is removed.

    .. seealso:: :ref:`skip`

    Args:
        id (int, optional): ID of the next test; must be greater than
            what would otherwise be the next test ID. For example, if
            the test immediately before this function is called was 42.5,
            ``id`` must be greater than 6 because 42.6 would already be
            the next test. If omitted, one test will be skipped.
    """
    # Advance the test number normally without creating a test. This call
    # also supports the skip-forward validation below by initializing
    # any zero IDs to one.
    get_id()

    if id is not None:
        if not isinstance(id, int):
            raise error.UserScriptError(
                f"Invalid id data type: {type(id).__name__}",
                "id must be an integer.",
            )
        if id <= state.current_id[-1]:
            raise error.UserScriptError(
                f"Invalid id value: {id}",
                f"Select an id greater than {state.current_id[-1]}.",
            )

        # The current ID is set to one previous because the get_id() call
        # above already increments the ID. The next test will then be assigned
        # the given id value because get_id() increments before returning
        # the assigned ID.
        state.current_id[-1] = id - 1
