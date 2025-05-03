"""Tests for defined term functions."""

import unittest

import atform
from atform.error import UserScriptError
from tests import utils


class Text(unittest.TestCase):
    """Tests for the add_term() text argument."""

    def test_invalid_type(self):
        """Confirm exception for a non-string."""
        with self.assertRaises(UserScriptError):
            atform.add_term(0, "label")


class Typeface(unittest.TestCase):
    """Tests for the add_term() typeface argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("term", "label", typeface=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("term", "label", typeface="foo")


class Font(unittest.TestCase):
    """Tests for the add_term() font argument."""

    def test_type(self):
        """Confirm exception for a non-string argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("term", "label", font=42)

    def test_undefined(self):
        """Confirm exception for an undefined argument."""
        with self.assertRaises(UserScriptError):
            atform.add_term("term", "label", font="foo")


class ContentArea(utils.ContentAreaException):
    """Tests confirming exception if add_term() is called outside the setup area."""

    @staticmethod
    def call():
        atform.add_term("term", "label")


class LabelReplacement(unittest.TestCase):
    """Tests for term label substitution."""

    def setUp(self):
        utils.reset()
        atform.add_term("foo", "term")

    def test_objective(self):
        """Confirm term label replacement in the objective."""
        atform.add_test("title", objective="$term")
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("foo", t.objective)

    def test_precondition(self):
        """Confirm term label replacement in the preconditions."""
        atform.add_test("title", preconditions=["p1 $term", "p2 $term"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("p1 foo", t.preconditions[0])
        self.assertEqual("p2 foo", t.preconditions[1])

    def test_procedure_text(self):
        """Confirm term label replacement in procedure text."""
        atform.add_test("title", procedure=["s1 $term", "s2 $term"])
        t = utils.get_test_content()
        t.pregenerate()
        self.assertEqual("s1 foo", t.procedure[0].text)
        self.assertEqual("s2 foo", t.procedure[1].text)


class SupportingTests(unittest.TestCase):
    """Tests for detecting supporting tests."""

    def setUp(self):
        utils.reset()
        atform.add_term("term1", "t1")
        atform.add_term("term2", "t2")

    def test_use_before_support(self):
        """Confirm """
