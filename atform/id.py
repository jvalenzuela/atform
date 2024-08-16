# This module manages the numeric identifiers assigned to each test.


from . import error
from . import misc


# Fields assigned to the most recent test.
current_id = [0]


# Section titles, keyed by ID tuple.
section_titles = {}


def get_id():
    """Returns the identifier to be used for the next test."""
    global current_id
    current_id[-1] = current_id[-1] + 1 # Increment last ID level for each test.

    # Initialize section levels that have been reset(0) to one.
    for i in range(0, len(current_id)):
        if current_id[i] == 0:
            current_id[i] = 1

    return tuple(current_id)


def to_string(id):
    """Generates a presentation string for a given ID tuple."""
    return '.'.join([str(x) for x in id])


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def section(level, id=None, title=None):
    """Creates a new section or subsection.

    The target section level is incremented, and the new section can be given
    an optional title. All subsections after the target level and individual
    test numbers will be reset.

    Args:
        level (int): Target identifier level in which to start a new section;
            must be greater than zero and less than the number of levels
            configured with :py:func:`atform.set_id_depth` because the
            highest level represents individual tests, not sections.
        id (int, optional): Target section value; target section is incremented
            by one if omitted. If specified, it must result in a jump
            forward relative to the current section, i.e., jumping backwards,
            or even to the current section, is not permitted.
        title (str, optional): Section title. Must only contain characters
            allowed in file system folder names.
    """
    global current_id
    global section_titles

    if len(current_id) == 1:
        raise error.UserScriptError(
            'No section levels available',
            """This function cannot be used unless the test ID depth is
            first increased with atform.set_id_depth to allow tests to be
            divided into sections."""
        )

    if not isinstance(level, int):
        raise error.UserScriptError('Section level must be an integer.')

    section_levels = range(1, len(current_id))
    if not level in section_levels:
        raise error.UserScriptError(
            f"Invalid section level: {level}",
            f"Use a section level between 1 and {section_levels[-1]}, "
            "inclusive."
        )

    # Convert the one-based level to a zero-based index suitable for
    # indexing current_id[].
    id_index = level - 1

    # Increment the target ID level.
    if id is None:
        current_id[id_index] = current_id[id_index] + 1

    # Jump to a specific number.
    else:
        if not isinstance(id, int):
            raise error.UserScriptError('id must be an integer.')
        elif id <= current_id[id_index]:
            raise error.UserScriptError(
                f"Invalid id value.",
                f"Level {level} id must be greater than {current_id[id_index]}."
            )
        current_id[id_index] = id

    # Reset higher ID levels.
    for i in range(id_index + 1, len(current_id)):
        current_id[i] = 0

    if title is not None:
        if not isinstance(title, str):
            raise error.UserScriptError('Section title must be a string.')
        section = tuple(current_id[:id_index + 1])
        stripped = title.strip()
        if stripped:
            section_titles[section] = stripped


@error.exit_on_script_error
@misc.setup_only
def set_id_depth(levels):
    """Configures the number of fields in test numeric identifiers.

    For example, setting the depth to three will generate identifiers with
    three numeric fields, like 2.1.1 or 4.2.3. This should be called once
    before any tests or sections are created.

    Args:
        levels (int): Number of identifier levels.
    """
    global current_id
    if not isinstance(levels, int):
        raise error.UserScriptError('Identifier depth must be an integer.')
    if levels < 1:
        raise error.UserScriptError(
            f"Invalid identifier depth value: {levels}",
            'Select an identifier depth greater than zero.'
        )
    current_id = [0] * levels


@error.exit_on_script_error
def skip_test(id=None):
    """Omits one or more tests.

    This function can only skip tests within the current section, i.e.,
    it will only affect the last identifier field. Typical usage is to
    reserve a range of IDs or maintain numbering if a test is removed.

    Args:
        id (int, optional): ID of the next test. If omitted, one test will
            be skipped.
    """
    global current_id

    # Advance the test number normally without creating a test. This call
    # also supports the skip-forward validation below by initializing
    # any zero IDs to one.
    get_id()

    if id is not None:
        if not isinstance(id, int):
            raise error.UserScriptError('id must be an integer.')
        if id <= current_id[-1]:
            raise error.UserScriptError(
                f"Invalid id value: {id}",
                f"Select an id greater than {current_id[-1]}."
            )

        # The current ID is set to one previous because the get_id() call
        # above already increments the ID. The next test will then be assigned
        # the given id value because get_id() increments before returning
        # the assigned ID.
        current_id[-1] = id - 1
