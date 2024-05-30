# This module manages the numeric identifiers assigned to each test.


# Fields that will be assigned as the next test's identifier.
next_id = [1]


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
    before any tests are created.

    :param int levels: Number of identifier levels.
    :raises ValueError: If levels is less than one.
    :raises TypeError: If levels is not an integer.
    :raises RuntimeError: If this function is called after one or more tests
                          have been created.
    """
    global next_id
    if not isinstance(levels, int):
        raise TypeError('Identifier depth must be an integer.')
    if levels < 1:
        raise ValueError('Identifier depth must be greater than zero.')
    if next_id.count(1) != len(next_id):
        raise RuntimeError(
            'Identifer depth cannot be altered after tests have been created.')
    next_id = [1] * levels
