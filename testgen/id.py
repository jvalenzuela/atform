# This module manages the numeric identifiers assigned to each test.


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
    if current_id.count(0) != len(current_id):
        raise RuntimeError(
            'Identifer depth cannot be altered after creating tests or sections.')

    current_id = [0] * levels
