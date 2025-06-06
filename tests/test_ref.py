# Unit tests for the ref module.


from tests import utils
import atform
import string
import unittest


class TestAddReferenceCategory(unittest.TestCase):
    """Unit tests for the add_reference_category() function."""

    def setUp(self):
        utils.reset()

    def test_title_type(self):
        """Confirm exception for a title that is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category(42, "label")

    def test_empty_title(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category("", "label")

    def test_blank_title(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category(string.whitespace, "label")

    def test_title_strip(self):
        """Confirm surrounding whitespace is removed from the title."""
        atform.add_reference_category(
            string.whitespace + "foo" + string.whitespace, "label"
        )
        self.assertIn("foo", atform.state.ref_titles.values())

    def test_label_type(self):
        """Confirm exception for a label that is not a string."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category("foo", None)

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category("foo", "")

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category("foo", string.whitespace)

    def test_duplicate_label(self):
        """Confirm exception for duplicate label."""
        atform.add_reference_category("foo", "bar")
        with self.assertRaises(atform.error.UserScriptError):
            atform.add_reference_category("spam", "bar")

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from the label."""
        atform.add_reference_category(
            "foo", string.whitespace + "label" + string.whitespace
        )
        self.assertIn("label", atform.state.ref_titles)

    def test_storage(self):
        """Confirm title is properly stored keyed by label."""
        atform.add_reference_category("foo", "bar")
        self.assertEqual({"bar": "foo"}, atform.state.ref_titles)


class AddReferenceCategoryContentAreaException(utils.ContentAreaException):
    """
    Tests to confirm exceptions when calling add_reference_category()
    outside of the setup area.
    """

    @staticmethod
    def call():
        atform.add_reference_category("foo", "bar")


class GetXRef(unittest.TestCase):
    """Unit tests for the get_xref() function."""

    def setUp(self):
        utils.reset()

    def test_no_categories(self):
        """Confirm an empty dictionary if no categories are defined."""
        self.assertEqual({}, atform.get_xref())

    def test_no_refs(self):
        """Confirm a category with no references yields an empty dictionary."""
        atform.add_reference_category("References", "refs")
        self.assertEqual({"refs": {}}, atform.get_xref())

    def test_id_sorted(self):
        """Confirm tests are listed in sorted order."""
        atform.add_reference_category("References", "refs")
        for i in range(10):
            atform.add_test("Test X", references={"refs": ["A"]})
        self.assertEqual(
            {"refs": {"A": [str(i + 1) for i in range(10)]}}, atform.get_xref()
        )

    def test_multi_categories(self):
        """Confirm correct cross-reference with multiple categories."""
        atform.add_reference_category("Numbers", "num")
        atform.add_reference_category("Letters", "alpha")

        atform.add_test(
            "only numbers",
            references={
                "num": ["1", "2"],
            },
        )

        atform.add_test(
            "numbers & letters",
            references={
                "num": ["2", "3"],
                "alpha": ["a", "b"],
            },
        )

        atform.add_test(
            "only letters",
            references={
                "alpha": ["b", "c"],
            },
        )

        self.assertEqual(
            {
                "num": {
                    "1": ["1"],
                    "2": ["1", "2"],
                    "3": ["2"],
                },
                "alpha": {
                    "a": ["2"],
                    "b": ["2", "3"],
                    "c": ["3"],
                },
            },
            atform.get_xref(),
        )
