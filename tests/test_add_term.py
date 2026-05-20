"""Unit tests for the add_term() function."""

import string
import unittest

import atform
from atform.error import UserScriptError
from tests import test_label
from tests import utils


class Text(unittest.TestCase):
    """Tests for the text parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term(42, "label")

    def test_empty(self):
        """Confirm exception for an empty string."""
        with self.assertRaises(UserScriptError):
            atform.add_term("", "label")

    def test_blank(self):
        """Confirm exception for a string containing only whitespace."""
        with self.assertRaises(UserScriptError):
            atform.add_term(string.whitespace, "label")

    def test_case_sensitive(self):
        """Confirm terms differing only in case are accepted."""
        atform.add_term("foo", "t1")
        atform.add_term("Foo", "t2")

    def test_duplicate(self):
        """Confirm exception when defining a duplicate term."""
        for dup in ["foo bar", " foo bar ", "foo  bar"]:
            utils.reset()
            atform.add_term("foo bar", "foolabel")
            with self.subTest(dup=dup), self.assertRaises(UserScriptError):
                atform.add_term(dup, "spamlabel")


class Label(test_label.LabelString, unittest.TestCase):
    """Tests for the label argument."""

    def create_label(self, label):
        """Implementation required by the LabelString superclass."""
        atform.add_term("foo", label)


class Typeface(unittest.TestCase):
    """Unit tests for the typeface argument."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("foo", "foo", typeface=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("foo", "foo", typeface="foo")


class Font(unittest.TestCase):
    """Unit tests for the font argument."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("foo", "foo", font=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("foo", "foo", font="foo")


class ContentArea(utils.ContentAreaException):
    """Tests to confirm exceptions when called outside the setup area."""

    @staticmethod
    def call():
        """Required by abstract superclass to call the target method."""
        atform.add_term("text", "label")
