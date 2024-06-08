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
