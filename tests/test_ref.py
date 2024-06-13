# Unit tests for the ref module.


from tests import utils
import testgen
import string
import unittest


class TestAddReferenceCategory(unittest.TestCase):
    """Unit tests for the add_reference_category() function."""

    def setUp(self):
        utils.reset()

    def test_title_type(self):
        """Confirm exception for a title that is not a string."""
        with self.assertRaises(TypeError):
            testgen.add_reference_category(42, 'label')

    def test_empty_title(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(ValueError):
            testgen.add_reference_category('', 'label')

    def test_blank_title(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.add_reference_category(string.whitespace, 'label')

    def test_title_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        testgen.add_reference_category(
            string.whitespace + 'foo' + string.whitespace,
            'label')
        self.assertIn('foo', testgen.ref.titles.values())

    def test_label_type(self):
        """Confirm exception for a label that is not a string."""
        with self.assertRaises(TypeError):
            testgen.add_reference_category('foo', None)

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(ValueError):
            testgen.add_reference_category('foo', '')

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.add_reference_category('foo', string.whitespace)

    def test_duplicate_label(self):
        """Confirm exception for duplicate label."""
        testgen.add_reference_category('foo', 'bar')
        with self.assertRaises(ValueError):
            testgen.add_reference_category('spam', 'bar')

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from the label."""
        testgen.add_reference_category(
            'foo',
            string.whitespace + 'label' + string.whitespace)
        self.assertIn('label', testgen.ref.titles)

    def test_storage(self):
        """Confirm title is properly stored keyed by label."""
        testgen.add_reference_category('foo', 'bar')
        self.assertEqual({'bar':'foo'}, testgen.ref.titles)

    def test_after_setup(self):
        """Confirm exception if called after creating tests or sections."""
        testgen.id.current_id = [2] # Simulate a generated test.
        with self.assertRaises(RuntimeError):
            testgen.add_reference_category('foo', 'bar')
