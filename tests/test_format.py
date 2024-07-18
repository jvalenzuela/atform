# Unit tests for the format module.


import testgen
import unittest
import xml.etree.ElementTree as ElementTree


class FormatText(unittest.TestCase):
    """Unit tests for the format_text() text argument."""

    def test_type(self):
        """Confirm exception for non-string argument."""
        with self.assertRaises(TypeError):
            testgen.format_text(42)

    def test_element_text(self):
        """Confirm the returned XML element contains the original text."""
        root = ElementTree.fromstring(testgen.format_text('foo'))
        self.assertEqual('foo', root.text)


class FormatTypeface(unittest.TestCase):
    """Unit tests for the format_text() typeface argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(KeyError):
            testgen.format_text('', typeface=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(KeyError):
            testgen.format_text('', typeface='foo')


class FormatFont(unittest.TestCase):
    """Unit tests for the format_text() font argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(KeyError):
            testgen.format_text('', font=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(KeyError):
            testgen.format_text('', font='foo')
