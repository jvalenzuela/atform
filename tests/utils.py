# Miscellaneous unit test utilities.


import testgen


def reset():
    """Resets the testgen package back to its initial state.

    This is used because many testgen modules store configuration state
    in global variables, which are only initialized when first imported,
    while unit test cases require this initial condition many times
    after a single import.
    """
    testgen.id.next_id = [1]
