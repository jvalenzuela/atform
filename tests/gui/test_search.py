"""Unit tests for searching test content."""

import string
import unittest

import atform
from atform.gui import search
from .. import utils


class Sections(unittest.TestCase):
    """Tests to confirm searching is limited to selected sections.

    Each case is composed of two tests: a positive match with only the
    target section containing the target text, and a negative match with
    all other sections containing the target text.
    """

    def setUp(self):
        utils.reset()
        atform.add_field("foo", 1, "foo", active=False)
        atform.add_reference_category("foo", "foo")

    def test_title(self):
        """Confirm content is located in the title."""
        atform.add_test("foo")
        atform.add_test(
            "title",
            active_fields=["foo"],
            objective="foo",
            references={"foo": ["foo"]},
            equipment=["foo"],
            preconditions=["foo"],
            procedure=["foo"],
        )
        self.assert_match("Title")

    def test_objective(self):
        """Confirm content is located in the objective."""
        atform.add_test("title", objective="foo")
        atform.add_test(
            "foo",
            active_fields=["foo"],
            references={"foo": ["foo"]},
            equipment=["foo"],
            preconditions=["foo"],
            procedure=["foo"],
        )
        self.assert_match("Objective")

    def test_references(self):
        """Confirm content is located in the references."""
        atform.add_test("title", references={"foo": ["foo"]})
        atform.add_test(
            "foo",
            active_fields=["foo"],
            objective="foo",
            equipment=["foo"],
            preconditions=["foo"],
            procedure=["foo"],
        )
        self.assert_match("References")

    def test_environment(self):
        """Confirm content is located in environment entry fields."""
        atform.add_test("title", active_fields=["foo"])
        atform.add_test(
            "foo",
            objective="foo",
            references={"foo": ["foo"]},
            equipment=["foo"],
            preconditions=["foo"],
            procedure=["foo"],
        )
        self.assert_match("Environment")

    def test_equipment(self):
        """Confirm content is located in the equipment list."""
        atform.add_test("title", equipment=["foo"])
        atform.add_test(
            "foo",
            active_fields=["foo"],
            objective="foo",
            references={"foo": ["foo"]},
            preconditions=["foo"],
            procedure=["foo"],
        )
        self.assert_match("Equipment")

    def test_preconditions(self):
        """Confirm content is located in the preconditions list."""
        atform.add_test("title", preconditions=["foo"])
        atform.add_test(
            "foo",
            active_fields=["foo"],
            objective="foo",
            references={"foo": ["foo"]},
            equipment=["foo"],
            procedure=["foo"],
        )
        self.assert_match("Preconditions")

    def test_procedure(self):
        """Confirm content is located in the procedure list."""
        atform.add_test("title", procedure=["foo"])
        atform.add_test(
            "foo",
            active_fields=["foo"],
            objective="foo",
            references={"foo": ["foo"]},
            equipment=["foo"],
            preconditions=["foo"],
        )
        self.assert_match("Procedure")

    def assert_match(self, section):
        """Confirms the text was found only in the target section."""
        tcs = search.TestContentSearch()
        matches = tcs.search("foo", [section], "all", False)
        self.assertEqual({(1,)}, matches)


class References(unittest.TestCase):
    """Tests for searching each component of a reference."""

    def setUp(self):
        utils.reset()

    def test_category_name(self):
        """Confirm the category name is searched."""
        atform.add_reference_category("foo", "foo")
        atform.add_test("title", references={"foo": ["bar"]})
        self.assert_match()

    def test_item(self):
        """Confirm reference items are searched."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("title", references={"ref": ["foo"]})
        self.assert_match()

    def assert_match(self):
        """Confirms the text was found in the references section."""
        tcs = search.TestContentSearch()
        matches = tcs.search("foo", ["References"], "all", False)
        self.assertEqual({(1,)}, matches)


class Procedure(unittest.TestCase):
    """Tests for searching procedure step components."""

    def setUp(self):
        utils.reset()

    def test_text(self):
        """Confirm step text is searched."""
        atform.add_test("title", procedure=["foo"])
        self.assert_match()

    def test_field_title(self):
        """Confirm data entry field titles are searched."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "text",
                    "fields": [("foo", 1)],
                },
            ],
        )
        self.assert_match()

    def test_field_suffix(self):
        """Confirm data entry field suffixes are searched."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "text",
                    "fields": [("f1", 1, "foo")],
                },
            ],
        )
        self.assert_match()

    def assert_match(self):
        """Confirms the text was found in the procedure section."""
        tcs = search.TestContentSearch()
        matches = tcs.search("foo", ["Procedure"], "all", False)
        self.assertEqual({(1,)}, matches)


class MultipleMatch(unittest.TestCase):
    """Tests for searches returning more than one match."""

    def setUp(self):
        utils.reset()

    def test_multiple(self):
        """Confirm all matching test IDs are returned."""
        atform.add_test("foo")
        atform.add_test("spam")
        atform.add_test("bar")
        tcs = search.TestContentSearch()
        matches = tcs.search("foo bar", ["Title"], "any", False)
        self.assertEqual({(1,), (3,)}, matches)


class CaseMatchingBase:
    """Base class for case matching tests.

    Each test case is performed by defining two test documents for each
    content section: one with the original text, and a second with the
    text in lower-case. Subclasses define the case matching option and
    which of the two tests should match.
    """

    # Target search text; must include upper-case letters.
    TEXT = "Foo"

    def setUp(self):
        utils.reset()

    def test_title(self):
        """Confirm content is located in the title."""
        atform.add_test(self.TEXT)
        atform.add_test(self.TEXT.lower())
        self.assert_match()

    def test_objective(self):
        """Confirm content is located in the objective."""
        atform.add_test("title", objective=self.TEXT)
        atform.add_test("title", objective=self.TEXT.lower())
        self.assert_match()

    def test_references(self):
        """Confirm content is located in the references."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("title", references={"ref": [self.TEXT]})
        atform.add_test("title", references={"ref": [self.TEXT.lower()]})
        self.assert_match()

    def test_environment(self):
        """Confirm content is located in environment entry fields."""
        atform.add_field(self.TEXT, 1, "f1", active=False)
        atform.add_field(self.TEXT.lower(), 1, "f2", active=False)
        atform.add_test("title", active_fields=["f1"])
        atform.add_test("title", active_fields=["f2"])
        self.assert_match()

    def test_equipment(self):
        """Confirm content is located in the equipment list."""
        atform.add_test("title", equipment=[self.TEXT])
        atform.add_test("title", equipment=[self.TEXT.lower()])
        self.assert_match()

    def test_preconditions(self):
        """Confirm content is located in the preconditions list."""
        atform.add_test("title", preconditions=[self.TEXT])
        atform.add_test("title", preconditions=[self.TEXT.lower()])
        self.assert_match()

    def test_procedure(self):
        """Confirm content is located in the procedure list."""
        atform.add_test("title", procedure=[self.TEXT])
        atform.add_test("title", procedure=[self.TEXT.lower()])
        self.assert_match()

    def assert_match(self):
        """Confirms text was found in the correct tests."""
        tcs = search.TestContentSearch()
        matches = tcs.search(
            self.TEXT,
            [
                "Title",
                "Objective",
                "References",
                "Environment",
                "Equipment",
                "Preconditions",
                "Procedure",
            ],
            "all",
            self.MATCH_CASE,
        )
        self.assertEqual(self.MATCHES, matches)


class CaseSensitive(CaseMatchingBase, unittest.TestCase):
    """Case-sensitive matching tests."""

    MATCH_CASE = True
    MATCHES = {(1,)}  # Only the test with original text should match.


class CaseInsensitive(CaseMatchingBase, unittest.TestCase):
    """Case-insensitive matching tests."""

    MATCH_CASE = False
    MATCHES = {(1,), (2,)}  # All defined tests should match.


class MatchAll(unittest.TestCase):
    """Tests for matching all terms."""

    def setUp(self):
        utils.reset()

    def test_single_field(self):
        """Confirm match when terms are in the same field."""
        atform.add_test("foo spam bar")
        atform.add_test("foo")
        self.assert_match("foo bar", {(1,)})

    def test_multiple_fields(self):
        """Confirm match when terms are spread across multiple fields."""
        atform.add_test("foo", objective="bar")
        atform.add_test("foo")
        self.assert_match("foo bar", {(1,)})

    def test_missing_term(self):
        """Confirm no match when all terms are not present."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.assert_match("foo bar", set())

    def assert_match(self, text, expected):
        """Confirms text was matched in the correct tests."""
        tcs = search.TestContentSearch()
        matches = tcs.search(
            text,
            [
                "Title",
                "Objective",
                "References",
                "Environment",
                "Equipment",
                "Preconditions",
                "Procedure",
            ],
            atform.gui.search.Grouping.ALL,
            False,
        )
        self.assertEqual(expected, matches)


class MatchAny(unittest.TestCase):
    """Tests for matching any terms."""

    def setUp(self):
        utils.reset()

    def test_some_terms(self):
        """Confirm match if some terms are present."""
        atform.add_test("bar")
        atform.add_test("spam eggs")
        self.assert_match("foo bar", {(1,)})

    def test_all_terms(self):
        """Confirm match if all terms are present."""
        atform.add_test("bar foo")
        atform.add_test("spam eggs")
        self.assert_match("foo bar", {(1,)})

    def test_no_match(self):
        """Confirm no match if none of the terms are present."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.assert_match("spam eggs", set())

    def assert_match(self, text, expected):
        """Confirms text was matched in the correct tests."""
        tcs = search.TestContentSearch()
        matches = tcs.search(
            text,
            ["Title"],
            atform.gui.search.Grouping.ANY,
            False,
        )
        self.assertEqual(expected, matches)


class Format(unittest.TestCase):
    """Tests to confirm content within format markup is found."""

    def setUp(self):
        utils.reset()

    def test_bullet_list(self):
        """Confirm text within a bullet list is found."""
        atform.add_test("title", objective=atform.bullet_list("foo", "bar"))
        self.assert_match("foo bar")

    def test_format(self):
        """Confirm formatted text is found."""
        atform.add_test("title", objective=atform.format_text("foo", font="bold"))
        self.assert_match("foo")

    def assert_match(self, text):
        """Confirms text was matched in the correct tests."""
        tcs = search.TestContentSearch()
        matches = tcs.search(text, ["Objective"], "all", False)
        self.assertEqual({(1,)}, matches)


class Phrase(unittest.TestCase):
    """Tests for queries containing quoted multi-word phrases."""

    def setUp(self):
        utils.reset()

    def test_whitespace_separator(self):
        """Confirm matches with terms separated by various whitespace."""
        for sep in string.whitespace:
            utils.reset()
            with self.subTest(sep=sep):
                title = sep.join(["foo", "bar"])
                atform.add_test(title)
                self.assert_match('"foo bar"', {(1,)})

    def test_partial(self):
        """Confirm no match for only part of the phrase."""
        atform.add_test("foo")
        atform.add_test("bar")
        self.assert_match('"foo bar"', set())

    def test_out_of_order(self):
        """Confirm no match for phrase terms in the wrong order."""
        atform.add_test("bar foo")
        self.assert_match('"foo bar"', set())

    def test_nonmatch_separator(self):
        """Confirm no match for terms separated by a non-matching term."""
        atform.add_test("foo spam bar")
        self.assert_match('"foo bar"', set())

    def assert_match(self, text, expected):
        """Confirms text was matched in the correct tests."""
        tcs = search.TestContentSearch()
        matches = tcs.search(text, ["Title"], "any", False)
        self.assertEqual(expected, matches)
