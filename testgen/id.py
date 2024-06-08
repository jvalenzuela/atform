# This module manages the numeric identifiers assigned to each test.


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


def section(level, id=None, title=None):
    """
    Creates a new section or subsection, incrementing the identifier, and
    optionally assigning a section title. All subsections after the
    target level and individual test numbers will be reset.

    Below is an example to help illustrate usage:

    ::

        testgen.set_id_depth(3) # Configure IDs as x.y.z.

        # Create tests; assume last test created was 1.1.5.

        testgen.section(0, title='Important Tests') # Increment to 2.y.z.

        # Tests here will begin at 2.1.1.

        testgen.section(1, id=10, title='Another Subsection') # Jump to x.10.z.

        # Tests here will begin at 2.10.1.

    :param int level: Zero-based index of the target identifier level in
                      which to start a new section.
    :param int id: Optional section value; target section is incremented
                   by one if omitted. If specified, it must result in a jump
                   forward relative to the current section, i.e., jumping
                   backwards, or even to the current section, is not
                   permitted.
    :param str title: Optional title. Must only contain characters allowed
                      in file system folder names.
    :raises ValueError: If level is not a valid section level, or id is not
                        greater than the current section.
    :raises TypeError: If level or id are not integers, or name is not a string.
    """
    global current_id
    global section_titles
    if not isinstance(level, int):
        raise TypeError('Section level must be an integer.')

    section_levels = range(0, len(current_id) - 1)
    if not level in section_levels:
        msg = "{0} is not a valid section level.".format(level)
        if len(current_id) > 1:
            msg = msg + " Valid sections are 0-{0} inclusive.".format(
                section_levels[-1])
        raise ValueError(msg)

    # Increment the target ID level.
    if id is None:
        current_id[level] = current_id[level] + 1

    # Jump to a specific number.
    else:
        if not isinstance(id, int):
            raise TypeError('id must be an integer.')
        elif id <= current_id[level]:
            raise ValueError(
                "Level {0} id must be greater than {1}.".format(
                    level,
                    current_id[level]))
        current_id[level] = id

    # Reset higher ID levels.
    for i in range(level + 1, len(current_id)):
        current_id[i] = 0

    if title is not None:
        if not isinstance(title, str):
            raise TypeError('Section title must be a string.')
        section = tuple(current_id[:level + 1])
        stripped = title.strip()
        if stripped:
            section_titles[section] = stripped


@misc.setup_only
def set_id_depth(levels):
    """
    Configures the number of fields for the identifier assigned to each test.
    For example, setting the depth to three will generate identifiers with
    three numeric fields, like 2.1.1 or 4.2.3. This should be called once
    before any tests or sections are created.

    :param int levels: Number of identifier levels.
    :raises ValueError: If levels is less than one.
    :raises TypeError: If levels is not an integer.
    :raises RuntimeError: If this function is called after any tests or
                          sections have been created.
    """
    global current_id
    if not isinstance(levels, int):
        raise TypeError('Identifier depth must be an integer.')
    if levels < 1:
        raise ValueError('Identifier depth must be greater than zero.')
    current_id = [0] * levels


def skip_test(id=None):
    """
    Omits one or more tests. This function can only skip tests within the
    current section, i.e., it will only affect the last identifier field.
    Typical usage, as shown below, is to reserve a range of IDs or
    maintain numbering if a test is removed.

    ::

        testgen.set_id_depth(2) # Configure IDs as x.y.

        # Create tests, assume up to 1.10.

        testgen.skip_test() # Omit 1.11.

        # Next test will be 1.12.

        testgen.skip_test(100)

        # Next test will be 1.100.

    :param int id: Optional ID of the next test. If omitted, one test
                   will be skipped.
    :raises ValueError: If id does not yield a skip forward. This includes
                        setting id to what would normally be the next test,
                        i.e., skipping zero tests.
    :raises TypeError: If id is not an integer.
    """
    global current_id

    # Advance the test number normally without creating a test. This call
    # also supports the skip-forward validation below by initializing
    # any zero IDs to one.
    get_id()

    if id is not None:
        if not isinstance(id, int):
            raise TypeError('id must be an integer.')
        if id <= current_id[-1]:
            raise ValueError("id must be greater than {0}.".format(
                current_id[-1]))

        # The current ID is set to one previous because the get_id() call
        # above already increments the ID. The next test will then be assigned
        # the given id value because get_id() increments before returning
        # the assigned ID.
        current_id[-1] = id - 1
