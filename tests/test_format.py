# Unit tests for the format module.


import atform
import unittest
import xml.etree.ElementTree as ElementTree


class BulletList(unittest.TestCase):
    """Unit tests for the bullet_list() function."""

    def test_item_type(self):
        """Confirm exception for non-string arguments."""
        with self.assertRaises(TypeError):
            atform.bullet_list(['foo', 'bar'])


class FormatText(unittest.TestCase):
    """Unit tests for the format_text() text argument."""

    def test_type(self):
        """Confirm exception for non-string argument."""
        with self.assertRaises(TypeError):
            atform.format_text(42)

    def test_element_text(self):
        """Confirm the returned XML element contains the original text."""
        root = ElementTree.fromstring(atform.format_text('foo'))
        self.assertEqual('foo', root.text)


class FormatTypeface(unittest.TestCase):
    """Unit tests for the format_text() typeface argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(KeyError):
            atform.format_text('', typeface=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(KeyError):
            atform.format_text('', typeface='foo')


class FormatFont(unittest.TestCase):
    """Unit tests for the format_text() font argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(KeyError):
            atform.format_text('', font=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(KeyError):
            atform.format_text('', font='foo')
