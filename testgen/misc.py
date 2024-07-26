from . import id
import functools


# The current project information set by the most recent call to
# set_project_info().
project_info = {}


def setup_only(func):
    """
    Decorator for public API functions that can only be called during setup,
    i.e., before any test or sections.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Setup area is determined by the current ID containing all zeros as
        # any new test or section will increment the current ID.
        in_setup = id.current_id.count(0) == len(id.current_id)

        if not in_setup:
            raise RuntimeError(
                func.__name__
                + " can only be called before creating tests or sections."
            )

        func(*args, *kwargs)

    return wrapper


def nonempty_string(name, s):
    """Checks a string to ensure it is not empty or blank."""
    if not isinstance(s, str):
        raise TypeError("{0} must be a string.".format(name))
    stripped = s.strip()
    if not stripped:
        raise ValueError("{0} cannot be empty.".format(name))
    return stripped


def validate_field_length(length):
    """Validates a data entry field length."""
    if not isinstance(length, int):
        raise TypeError('Field length must be an integer.')
    if length < 1:
        raise ValueError('Field length must be greater than zero.')
    return length


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


def set_project_info(project=None, system=None):
    """Assigns project metadata.

    Information set by this function is used to populate the headers
    and footers. May be used in both setup and content areas.

    .. seealso:: :ref:`project_info`

    Args:
        project (str, optional): Name or description of the project.
        system (str, optional): Name or description of the system being tested.

    Raises:
        TypeError
        ValueError
    """
    global project_info
    params = locals()
    for arg in params:
        if params[arg] is not None:
            project_info[arg] = nonempty_string(arg, params[arg])
