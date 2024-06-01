# This module manages the numeric identifiers assigned to each test.


# Fields assigned to the most recent test.
current_id = [0]


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
