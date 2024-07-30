# Unit tests for the label module.


from tests import utils
from atform import label
import string
import unittest


class Add(unittest.TestCase):
    """Tests for the add() function."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string label."""
        with self.assertRaises(TypeError):
            label.add(42, 'id')

    def test_empty(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(ValueError):
            label.add('', 'id')

    def test_blank(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(ValueError):
            label.add(string.whitespace, 'id')

    def test_leading_whitespace(self):
        """Confirm exception for a label containing leading whitespace."""
        with self.assertRaises(ValueError):
            label.add(string.whitespace + 'foo', 'id')

    def test_trailing_whitespace(self):
        """Confirm exception for a label containing trailing whitespace."""
        with self.assertRaises(ValueError):
            label.add('foo' + string.whitespace, 'id')

    def test_middle_whitespace(self):
        """Confirm exception for a label with whitespace in the middle."""
        with self.assertRaises(ValueError):
            label.add('foo' + string.whitespace + 'bar', 'id')

    def test_punctuation(self):
        """Confirm exception for a label with punctuation other than underscore."""
        punc = set(string.punctuation)
        punc.remove('_')
        for p in punc:
            with self.assertRaises(
                    ValueError,
                    msg="Failed for '{0}'".format(p)
            ):
                label.add('foo' + p, 'id')

    def test_duplicate(self):
        """Confirm exception for duplicate labels."""
        label.add('foo', 'id')
        with self.assertRaises(ValueError):
            label.add('foo', 'id')


class Resolve(unittest.TestCase):
    """Unit tests for the resolve() function."""

    def setUp(self):
        utils.reset()

    def test_undefined_label(self):
        """Confirm exception for a string with an undefined label."""
        with self.assertRaises(KeyError):
            label.resolve('$foo')

    def test_invalid_identifier(self):
        """Confirm exception for a string with an invalid identifier."""
        with self.assertRaises(ValueError):
            label.resolve('$ foo')

    def test_no_identifiers(self):
        """Confirm a string with no identifiers is returned unmodified."""
        s = 'foo'
        self.assertEqual(s, label.resolve(s))

    def test_replacement(self):
        """Confirm labels are replaced with their IDs."""
        label.add('spam', 'foo')
        label.add('eggs', 'bar')
        self.assertEqual('foo bar', label.resolve('$spam $eggs'))
