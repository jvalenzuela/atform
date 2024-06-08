# Unit tests for the sig module.


from tests import utils
import testgen
import string
import unittest


class AddSignature(unittest.TestCase):
    """Unit tests for the add_signature() function."""

    def setUp(self):
        utils.reset()

    def test_after_content(self):
        """Confirm exception if called after a test or section is created."""
        testgen.id.current_id = [2] # Simulate a generated test.
        with self.assertRaises(RuntimeError):
            testgen.add_signature('foo')

    def test_title_type(self):
        """Confirm exception for a non-string title."""
        with self.assertRaises(TypeError):
            testgen.add_signature(99)

    def test_empty_title(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(ValueError):
            testgen.add_signature('')

    def test_blank_title(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.add_signature(string.whitespace)

    def test_title_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        testgen.add_signature(string.whitespace + "spam" + string.whitespace)
        self.assertEqual(['spam'], testgen.sig.titles)

    def test_title_order(self):
        """Confirm titles are added in the order defined."""
        expected = ['foo', 'bar', 'spam', 'eggs']
        [testgen.add_signature(s) for s in expected]
        self.assertEqual(expected, testgen.sig.titles)
