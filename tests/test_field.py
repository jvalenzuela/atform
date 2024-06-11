# Unit tests for the field module.


from tests import utils
import testgen
import string
import unittest


class AddField(unittest.TestCase):
    """Unit tests for the add_field() function."""

    def setUp(self):
        utils.reset()

    def test_title_type(self):
        """Confirm exception if title is not a string."""
        with self.assertRaises(TypeError):
            testgen.add_field(100, 1)

    def test_empty_title(self):
        """Confirm exception if title is empty."""
        with self.assertRaises(ValueError):
            testgen.add_field('', 1)

    def test_blank_title(self):
        """Confirm exception if title contains only whitespace."""
        with self.assertRaises(ValueError):
            testgen.add_field(string.whitespace, 1)

    def test_title_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        testgen.add_field(string.whitespace + 'foo bar' + string.whitespace, 1)
        self.assertEqual(1, testgen.field.lengths['foo bar'])

    def test_length_type(self):
        """Confirm exception if length is not an integer."""
        with self.assertRaises(TypeError):
            testgen.add_field('foo', '1')

    def test_length_out_of_range(self):
        """Confirm exception for lengths less than one."""
        with self.assertRaises(ValueError):
            testgen.add_field('foo', 0)

    def test_storage(self):
        """Confirm fields are stored in order."""
        orig = [('one', 1), ('two', 2), ('three', 3)]
        [testgen.add_field(*f) for f in orig]
        self.assertEqual([f[0] for f in orig],
                         list(testgen.field.lengths.keys()))
        [self.assertEqual(f[1], testgen.field.lengths[f[0]]) for f in orig]

    def test_after_test_created(self):
        """Confirm exception if called after creating tests."""
        testgen.id.current_id = [2] # Simulate a generated test.
        with self.assertRaises(RuntimeError):
            testgen.add_field('foo', 1)
