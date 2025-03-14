# Miscellaneous unit test utilities.


import atform
from atform import label
import collections
import unittest


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
