"""Tests for the get_term () API function."""

import collections
import unittest

import atform
from atform.error import UserScriptError
from tests import utils


@utils.no_pdf_output
@utils.disable_idlock
@utils.no_args
def generate():
    """Wrapper for atform.generate() to disable unnecessary side effects."""
    atform.generate()


class InvalidWhich(unittest.TestCase):
    """Tests for invalid which arguments."""

    def test_type(self):
        """Confirm exception for a non-string value."""
        with self.assertRaises(UserScriptError):
            atform.get_terms([42])

    def test_undefined_string(self):
        """Confirm exception for a string containing an undefined option."""
        with self.assertRaises(UserScriptError):
            atform.get_terms("foo")


class MultipleCall(unittest.TestCase):
    """Tests for calling get_term() multiple times."""

    def setUp(self):
        utils.reset()

    def test_return_identity(self):
        """Confirm each call returns a new dict instance."""
        generate()
        self.assertIsNot(atform.get_terms(), atform.get_terms())


class WhichBoth(unittest.TestCase):
    """Tests for selecting both supported and used terms."""

    def setUp(self):
        utils.reset()

    def test_default(self):
        """Confirm this is the default argument."""
        atform.add_term("foo", "term")
        atform.add_test("t1", supports_terms=["term"])
        atform.add_test("t2", objective="$term")
        both = self.result
        default = atform.get_terms()
        self.assertEqual(default, both)

    def test_no_terms(self):
        """Confirm result when no terms are defined."""
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_no_supported_or_use(self):
        """Confirm result for a term that is neither used or supported."""
        atform.add_term("foo", "term")
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_unsupported_use(self):
        """Confirm result for a term that is used but not supported."""
        atform.add_term("foo", "term")
        atform.add_test("title", objective="$term")
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_support_not_used(self):
        """Confirm result for a supported term that is not used elsewhere."""
        atform.add_term("foo", "term")
        atform.add_test("title", supports_terms=["term"])
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_support_and_used_same(self):
        """Confirm result for a term supported and used in the same test."""
        atform.add_term("foo", "term")
        atform.add_test("t1", objective="$term", supports_terms=["term"])
        self.assertEqual({"foo": ["1 t1"]}, self.result)

    def test_support_and_used_diff(self):
        """Confirm result for a term supported in one test and used in another."""
        atform.add_term("foo", "term")
        atform.add_test("t1", supports_terms=["term"])
        atform.add_test("t2", objective="$term")
        self.assertEqual({"foo": ["1 t1", "2 t2"]}, self.result)

    def test_multiple_support(self):
        """Confirm result when multiple tests support a single term."""
        atform.add_term("foo", "term")
        atform.add_test("s1", supports_terms=["term"])
        atform.add_test("s2", supports_terms=["term"])
        self.assertEqual({"foo": ["1 s1", "2 s2"]}, self.result)

    def test_multiple_use(self):
        """Confirm result when a term is used in mulitple tests."""
        atform.add_term("foo", "term")
        atform.add_test("t1", objective="$term")
        atform.add_test("t2", objective="$term")
        self.assertEqual({"foo": ["1 t1", "2 t2"]}, self.result)

    def test_unformatted(self):
        """Confirm the raw text is returned for a formatted term."""
        atform.add_term("foo", "term", font="bold")
        atform.add_test("title", objective="$term")
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_order(self):
        """Confirm returned terms are ordered."""
        atform.add_term("b", "t1")
        atform.add_term("c", "t2")
        atform.add_term("a", "t3")
        atform.add_test("title", supports_terms=["t1", "t2", "t3"])
        result = self.result
        self.assertIsInstance(result, collections.OrderedDict)
        self.assertEqual(["a", "b", "c"], list(result.keys()))

    @property
    def result(self):
        """Gets the result returned from get_terms()."""
        generate()
        return atform.get_terms("both")


class WhichSupport(unittest.TestCase):
    """Tests for selecting supported terms only."""

    def setUp(self):
        utils.reset()

    def test_no_terms(self):
        """Confirm result when no terms are defined."""
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_no_supported_or_use(self):
        """Confirm result for a term that is neither used or supported."""
        atform.add_term("foo", "term")
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_unsupported_use(self):
        """Confirm result for a term that is used but not supported."""
        atform.add_term("foo", "term")
        atform.add_test("title", objective="$term")
        self.assertEqual({}, self.result)

    def test_support_not_used(self):
        """Confirm a supported term is returned when not used elsewhere."""
        atform.add_term("foo", "term")
        atform.add_test("title", supports_terms=["term"])
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_support_and_used_same(self):
        """Confirm result for a term supported and used in the same test."""
        atform.add_term("foo", "term")
        atform.add_test("t1", objective="$term", supports_terms=["term"])
        self.assertEqual({"foo": ["1 t1"]}, self.result)

    def test_support_and_used_diff(self):
        """Confirm result for a term supported in one test and used in another."""
        atform.add_term("foo", "term")
        atform.add_test("t1", supports_terms=["term"])
        atform.add_test("t2", objective="$term")
        self.assertEqual({"foo": ["1 t1"]}, self.result)

    def test_multiple_support(self):
        """Confirm result when multiple tests support a single term."""
        atform.add_term("foo", "term")
        atform.add_test("s1", supports_terms=["term"])
        atform.add_test("s2", supports_terms=["term"])
        self.assertEqual({"foo": ["1 s1", "2 s2"]}, self.result)

    def test_unformatted(self):
        """Confirm the raw text is returned for a formatted term."""
        atform.add_term("foo", "term", font="bold")
        atform.add_test("title", supports_terms=["term"])
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_order(self):
        """Confirm returned terms are ordered."""
        atform.add_term("b", "t1")
        atform.add_term("c", "t2")
        atform.add_term("a", "t3")
        atform.add_test("title", supports_terms=["t1", "t2", "t3"])
        result = self.result
        self.assertIsInstance(result, collections.OrderedDict)
        self.assertEqual(["a", "b", "c"], list(result.keys()))

    @property
    def result(self):
        """Gets the result returned from get_terms()."""
        generate()
        return atform.get_terms("support")


class WhichUse(unittest.TestCase):
    """Tests for selecting used terms only."""

    def setUp(self):
        utils.reset()

    def test_no_terms(self):
        """Confirm result when no terms are defined."""
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_no_use_or_support(self):
        """Confirm result for a term that is neither used or supported."""
        atform.add_term("foo", "term")
        atform.add_test("title")
        self.assertEqual({}, self.result)

    def test_supported_unused(self):
        """Confirm result for a supported term that is not otherwise used."""
        atform.add_term("foo", "term")
        atform.add_test("title", supports_terms=["term"])
        self.assertEqual({}, self.result)

    def test_used_unsupported(self):
        """Confirm result when a term is used but not supported."""
        atform.add_term("foo", "term")
        atform.add_test("title", objective="$term")
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_used_and_supported_same(self):
        """Confirm result for a term supported and used in the same test."""
        atform.add_term("foo", "term")
        atform.add_test("title", objective="$term", supports_terms=["term"])
        self.assertEqual({}, self.result)

    def test_used_and_supported_diff(self):
        """Confirm result for a term supported in one test and used in another."""
        atform.add_term("foo", "term")
        atform.add_test("t1", objective="$term")
        atform.add_test("t2", supports_terms=["term"])
        self.assertEqual({"foo": ["1 t1"]}, self.result)

    def test_multiple_use(self):
        """Confirm result when a term is used in mulitple tests."""
        atform.add_term("foo", "term")
        atform.add_test("t1", objective="$term")
        atform.add_test("t2", objective="$term")
        self.assertEqual({"foo": ["1 t1", "2 t2"]}, self.result)

    def test_unformatted(self):
        """Confirm the raw text is returned for a formatted term."""
        atform.add_term("foo", "term", font="bold")
        atform.add_test("title", objective="$term")
        self.assertEqual({"foo": ["1 title"]}, self.result)

    def test_order(self):
        """Confirm returned terms are ordered."""
        atform.add_term("b", "t1")
        atform.add_term("c", "t2")
        atform.add_term("a", "t3")
        atform.add_test("title", objective="$t1 $t2 $t3")
        result = self.result
        self.assertIsInstance(result, collections.OrderedDict)
        self.assertEqual(["a", "b", "c"], list(result.keys()))

    @property
    def result(self):
        """Gets the result returned from get_terms()."""
        generate()
        return atform.get_terms("use")
