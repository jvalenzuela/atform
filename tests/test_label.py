# Unit tests for the label module.


from tests import utils
from atform import label
from atform.error import UserScriptError
import string
import unittest


class Add(unittest.TestCase):
    """Tests for the add() function."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string label."""
        with self.assertRaises(UserScriptError):
            label.add(42, "id")

    def test_empty(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(UserScriptError):
            label.add("", "id")

    def test_blank(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(UserScriptError):
            label.add(string.whitespace, "id")

    def test_invalid_first_character(self):
        """Confirm exception for a label with an invalid first character."""
        invalid = set(string.printable)

        # Exclude valid characters.
        invalid.difference_update(string.ascii_letters)
        invalid.remove("_")

        for c in invalid:
            with self.subTest(c=c), self.assertRaises(UserScriptError):
                label.add(c + "foo", "id")

    def test_invalid_following_character(self):
        """Confirm exception for a label with an invalid character after the first."""
        invalid = set(string.printable)

        # Exclude valid characters.
        invalid.difference_update(string.ascii_letters)
        invalid.difference_update(string.digits)
        invalid.difference_update("_")

        for c in invalid:
            with self.subTest(c=c), self.assertRaises(UserScriptError):
                label.add("foo" + c, "id")

    def test_nonascii(self):
        """Confirm exception for a label containing non-ASCII characters."""
        with self.assertRaises(UserScriptError):
            label.add("foo\u00dfar", "id")

    def test_valid_single_character(self):
        """Confirm a valid single-character label is accepted."""
        valid = set(string.ascii_letters)
        valid.add("_")

        for c in valid:
            with self.subTest(c=c):
                label.add(c, "id")

    def test_valid_multi_character(self):
        """Confirm a valid multi-character label is accepted."""
        valid = set(string.ascii_letters)
        valid.update(string.digits)
        valid.add("_")

        for c in valid:
            with self.subTest(c=c):
                label.add("foo" + c, "id")

    def test_duplicate(self):
        """Confirm exception for duplicate labels."""
        label.add("foo", "id")
        with self.assertRaises(UserScriptError):
            label.add("foo", "id")


class Resolve(unittest.TestCase):
    """Unit tests for the resolve() function."""

    def setUp(self):
        utils.reset()

    def test_undefined_label(self):
        """Confirm exception for a string with an undefined label."""
        with self.assertRaises(UserScriptError):
            label.resolve("$foo")

    def test_invalid_identifier(self):
        """Confirm exception for a string with an invalid identifier."""
        with self.assertRaises(UserScriptError):
            label.resolve("$ foo")

    def test_no_identifiers(self):
        """Confirm a string with no identifiers is returned unmodified."""
        s = "foo"
        self.assertEqual(s, label.resolve(s))

    def test_replacement(self):
        """Confirm labels are replaced with their IDs."""
        label.add("spam", "foo")
        label.add("eggs", "bar")
        self.assertEqual("foo bar", label.resolve("$spam $eggs"))
