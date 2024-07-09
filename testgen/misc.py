from . import id
import functools


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
