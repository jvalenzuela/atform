# Miscellaneous unit test utilities.


import atform
from atform import label
import collections
import unittest
from unittest.mock import patch


def reset():
    """Resets the atform package back to its initial state.

    This is used because many atform modules store configuration state
    in global variables, which are only initialized when first imported,
    while unit test cases require this initial condition many times
    after a single import.
    """
    atform.state.init()

    # The image cache needs to be reset separately as it is not stored
    # in the state module.
    atform.image.load.cache_clear()


def get_test_content():
    """Retrieves the content of the most recently created test."""
    return atform.state.tests[-1]


def mock_build(test, *args):
    """Dummy PDF build function to inhibit generating actual output files."""
    return test.id, {"page count": 1}


def no_pdf_output(method):
    """Test case decorator to prevent generating unnecessary output files."""

    @patch("atform.gen.pdf.build", new=mock_build)
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)

    return wrapper


def disable_idlock(method):
    """Test case decorator to disable all ID lock file operations."""

    def wrapper(self, *args, **kwargs):
        with patch("atform.idlock.verify", return_value=None):
            method(self, *args, **kwargs)

    return wrapper


class ContentAreaException(unittest.TestCase):
    """
    Base class for testing functions only available in the setup area to
    ensure an exception is raised when called outside of setup.
    """

    def setUp(self):
        reset()

    def test_after_test_created(self):
        """Confirm exception if called after a test is created."""
        atform.add_test("title")
        with self.assertRaises(SystemExit):
            self.call()

    def test_after_section(self):
        """Confirm exception if called after a section is created."""
        atform.set_id_depth(2)
        atform.section(1)
        with self.assertRaises(SystemExit):
            self.call()


def wrap_arg_parse(orig_func):
    """Creates a wrapper for the command line argument parsing function.

    This is intended to handle internal calls to the parser function
    other than those directly testing the argument parser. By default,
    the parser evaluates sys.argv, which will not contain valid arguments
    during unit testing, so this provides a default argument to the original
    function ensuring sys.argv is never parsed during unit tests.

    Since the arg module's parse function needs to be replaced, this function
    utilizes a closure to retain a reference to the original callable within
    the returned wrapper function.
    """

    def wrapper(args=None):
        if args is None:
            args = []

        return orig_func(args)

    return wrapper


# Replace the argument parser function with a wrapper; see wrapper function
# comments for details.
atform.arg.parse = wrap_arg_parse(atform.arg.parse)
