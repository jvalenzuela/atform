# This module maintains user-defined form field configuration.


from . import error
from . import misc
import collections


# Length of each field, keyed by title, ordered as added by add_field().
lengths = collections.OrderedDict()


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
@misc.setup_only
def add_field(title, length):
    """Adds a user entry field to capture test execution information.

    Form fields are suitable for entering a single line of text at the beginning
    of each test; fields will be listed in the order they were added.
    This function can only be used in the setup area of the script,
    before any tests or sections are created.

    Args:
        title (str): Text to serve as the field's prompt; must not be blank.
        length (int): Maximum number of characters the field should be sized
            to accommodate; must be greater than zero.
    """
    global lengths
    if not isinstance(title, str):
        raise error.UserScriptError('Field title must be a string.')
    stripped = title.strip()
    if not stripped:
        raise error.UserScriptError(
            'Field title cannot be blank.',
            'Add printable characters to the title, or remove the field.',
        )
    lengths[stripped] = misc.validate_field_length(length)
