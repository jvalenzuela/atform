# Unit tests for the sig module.


from tests import utils
import atform
import string
import unittest


class AddSignature(unittest.TestCase):
    """Unit tests for the add_signature() function."""

    def setUp(self):
        utils.reset()

    def test_title_type(self):
        """Confirm exception for a non-string title."""
        with self.assertRaises(SystemExit):
            atform.add_signature(99)

    def test_empty_title(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(SystemExit):
            atform.add_signature('')

    def test_blank_title(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.add_signature(string.whitespace)

    def test_title_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        atform.add_signature(string.whitespace + "spam" + string.whitespace)
        self.assertEqual(['spam'], atform.sig.titles)

    def test_title_order(self):
        """Confirm titles are added in the order defined."""
        expected = ['foo', 'bar', 'spam', 'eggs']
        [atform.add_signature(s) for s in expected]
        self.assertEqual(expected, atform.sig.titles)


class AddSignatureContentArea(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling add_signature() outside of
    the setup area.
    """

    @staticmethod
    def call():
        atform.add_signature('foo')
