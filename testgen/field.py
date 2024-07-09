# This module maintains user-defined form field configuration.


from . import misc
import collections


# Length of each field, keyed by title, ordered as added by add_field().
lengths = collections.OrderedDict()


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@misc.setup_only
def add_field(title, length):
    """Adds a user entry field to capture test execution information.

    Form fields are suitable for entering a single line of text at the beginning
    of each test; fields will be listed in the order they were added.
    This function can only be used in the setup area of the script,
    before any tests or sections are created.

    ::

        # Add a field to capture the software version, such as a git SHA1.
        testgen.add_field('Software Version', 10)

        # Add a field to record the a two-digit vehicle number.
        testgen.add_field('Vehicle', 2)

    :param str title: Text to serve as the field's prompt; must not be blank.
    :param int length: Maximum number of characters the field should be
                       sized to accommodate; must be greater than zero.
    :raises TypeError: If the title is not a string or length is not an
                       integer.
    :raises ValueError: If length is less than one.
    :raises RuntimeError: If this function is called after any tests or
                          sections have been created.
    """
    global lengths
    if not isinstance(title, str):
        raise TypeError('Field title must be a string.')
    stripped = title.strip()
    if not stripped:
        raise ValueError('Field title cannot be blank.')
    lengths[stripped] = misc.validate_field_length(length)
