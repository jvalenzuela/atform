# Unit tests for the add_copyright() function.


from tests import utils
import atform
import string
import unittest


class AddCopyright(unittest.TestCase):

    def setUp(self):
        utils.reset()

    def test_notice_type(self):
        """Confirm exception for a non-string notice."""
        with self.assertRaises(SystemExit):
            atform.add_copyright(42)

    def test_empty_notice(self):
        """Confirm exception for an empty notice string."""
        with self.assertRaises(SystemExit):
            atform.add_copyright("")

    def test_blank_notice(self):
        """Confirm exception for a notice containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.add_copyright(string.whitespace)

    def test_multiple_call(self):
        """Confirm exception if function is called more than once."""
        atform.add_copyright("foo")
        with self.assertRaises(SystemExit):
            atform.add_copyright("bar")


class AddCopyrightContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions if add_copyright() is called outside the
    setup area.
    """

    @staticmethod
    def call():
        atform.add_copyright("spam")
