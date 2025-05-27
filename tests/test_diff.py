"""Unit tests for detecting tests changes via the --diff option."""

import os
import pickle
import unittest
from unittest.mock import mock_open, patch

import atform
from . import utils


class DiffBase(unittest.TestCase):
    """Base class for diff test cases.

    Each test case is composed of two calls to generate(): the first with
    old content, and the second with the diff option.
    """

    def setUp(self):
        utils.reset()

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    @patch("atform.cache.load")
    def generate_old(self, *args):
        """Wrapper for the first call to generate().

        Simulates a script run without the diff option to capture the
        original content, saving the cache data to be loaded on the
        second generate() call.
        """
        atform.cache.data = {}
        atform.generate()
        self.cache_data = atform.cache.data

        # The page counts cache is cumulative, i.e., only built IDs
        # get overwritten, so it needs to be explicitly emptied before
        # the diff run, which uses the page counts cache to determine
        # which IDs got built.
        self.cache_data["page counts"] = {}

        utils.reset()  # Reset in preparation for the second run.

    @utils.no_pdf_output
    @utils.disable_idlock
    @patch("atform.cache.load")
    def generate_diff(self, diff_ids, *args, id_args=None):
        """Wrapper for the second call to generate().

        Run with the diff option using the cache data from the first call.
        """
        atform.cache.data = self.cache_data

        # Assemble mock CLI arguments with --diff plus any optional IDs.
        argv = ["--diff"]
        if id_args:
            argv.append(id_args)

        with patch("sys.argv", utils.mock_argv(" ".join(argv))):
            atform.generate()

        # The page counts saved to the cache is used to determine which tests
        # were actually built.
        built_ids = set(atform.cache.data["page counts"].keys())

        self.assertEqual(diff_ids, built_ids)


class Copyright(DiffBase):
    """Tests for detecting changes to the copyright message."""

    def test_same(self):
        """Confirm no copyright change is not flagged as a difference."""
        atform.add_copyright("foo")
        atform.add_test("title")
        self.generate_old()

        atform.add_copyright("foo")
        atform.add_test("title")
        self.generate_diff(set())

    def test_add(self):
        """Confirm adding a copyright message is detected."""
        atform.add_test("title")
        self.generate_old()

        atform.add_copyright("foo")
        atform.add_test("title")
        self.generate_diff({(1,)})

    def test_remove(self):
        """Confirm removing the copyright message is detected."""
        atform.add_copyright("foo")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("title")
        self.generate_diff({(1,)})

    def test_change(self):
        """Confirm altering the copyright message is detected."""
        atform.add_copyright("foo")
        atform.add_test("title")
        self.generate_old()

        atform.add_copyright("bar")
        atform.add_test("title")
        self.generate_diff({(1,)})


class Logo(DiffBase):
    """Tests for detecting changes to the logo image."""

    def image_path(self, filename):
        """Generates a path to a logo image file."""
        return os.path.join("tests", "images", "logo", filename)

    def test_same(self):
        """Confirm no logo changes is not flagged as a difference."""
        atform.add_logo(self.image_path("full.jpg"))
        atform.add_test("title")
        self.generate_old()

        atform.add_logo(self.image_path("full.jpg"))
        atform.add_test("title")
        self.generate_diff(set())

    def test_add(self):
        """Confirm adding a logo is detected."""
        atform.add_test("title")
        self.generate_old()

        atform.add_logo(self.image_path("full.jpg"))
        atform.add_test("title")
        self.generate_diff({(1,)})

    def test_remove(self):
        """Confirm removing the logo is detected."""
        atform.add_logo(self.image_path("full.jpg"))
        atform.add_test("title")
        self.generate_old()

        atform.add_test("title")
        self.generate_diff({(1,)})

    def test_change(self):
        """Confirm changing the logo image is detected.

        This is done with mock image content instead of actual files to ensure
        the comparison is applied to the image content, not the file name,
        i.e., detecting a change to the image file itself, not its path.
        """
        with utils.mock_image("JPEG", (10, 10)):
            atform.add_logo("foo")
        atform.add_test("title")
        self.generate_old()

        with utils.mock_image("JPEG", (20, 20)):
            atform.add_logo("foo")
        atform.add_test("title")
        self.generate_diff({(1,)})


class Signature(DiffBase):
    """Tests for detecting changes to approval signatures."""

    def test_same(self):
        """Confirm no signature changes is not flagged as a difference."""
        atform.add_signature("sig")
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("sig")
        atform.add_test("test")
        self.generate_diff(set())

    def test_add_to_none(self):
        """Confirm adding a signature where none were previously defined is detected."""
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("sig")
        atform.add_test("test")
        self.generate_diff({(1,)})

    def test_add_to_existing(self):
        """Confirm adding a signature to an existing set of signatures is detected."""
        atform.add_signature("sig1")
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("sig1")
        atform.add_signature("sig2")
        atform.add_test("test")
        self.generate_diff({(1,)})

    def test_remove_all(self):
        """Confirm removing all signatures is detected."""
        atform.add_signature("sig")
        atform.add_test("test")
        self.generate_old()

        atform.add_test("test")
        self.generate_diff({(1,)})

    def test_remove_one(self):
        """Confirm removing one signature while others remain is detected."""
        atform.add_signature("sig1")
        atform.add_signature("sig2")
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("sig1")
        atform.add_test("test")
        self.generate_diff({(1,)})

    def test_change_title(self):
        """Confirm altering a signature title is detected."""
        atform.add_signature("sig")
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("foo")
        atform.add_test("test")
        self.generate_diff({(1,)})

    def test_change_order(self):
        """Confirm altering the signature order is detected."""
        atform.add_signature("sig1")
        atform.add_signature("sig2")
        atform.add_test("test")
        self.generate_old()

        atform.add_signature("sig2")
        atform.add_signature("sig1")
        atform.add_test("test")
        self.generate_diff({(1,)})


class ProjectInfo(DiffBase):
    """Tests for detecting changes to project information."""

    def test_same(self):
        """Confirm no project information changes is not flagged as a difference."""
        atform.set_project_info(project="prj", system="sys")
        atform.add_test("title")
        self.generate_old()

        atform.set_project_info(project="prj", system="sys")
        atform.add_test("title")
        self.generate_diff(set())

    def test_add_project(self):
        """Confirm adding a project name is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.set_project_info(project="prj")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_change_project(self):
        """Confirm altering the project name is detected."""
        atform.add_test("unchanged")
        atform.set_project_info(project="prj")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.set_project_info(project="foo")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_add_system(self):
        """Confirm adding a system name is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.set_project_info(system="sys")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_change_system(self):
        """Confirm altering the system name is detected."""
        atform.add_test("unchanged")
        atform.set_project_info(system="sys")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.set_project_info(system="foo")
        atform.add_test("title")
        self.generate_diff({(2,)})


class IdDepth(DiffBase):
    """Tests for detecting changes to ID depth."""

    def test_change(self):
        """Confirm changing the ID depth is detected."""
        atform.add_test("t1")
        atform.add_test("t2")
        self.generate_old()

        atform.set_id_depth(2)
        atform.add_test("t1")
        atform.add_test("t2")
        self.generate_diff({(1, 1), (1, 2)})


class AddRemoveTest(DiffBase):
    """Tests for detecting adding and removing entire tests."""

    def test_add(self):
        """Confirm adding a new test is detected."""
        atform.add_test("unchanged")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("new test")
        self.generate_diff({(2,)})

    def test_remove(self):
        """Confirm removing a test does not incorrectly mark other tests."""
        atform.add_test("unchanged")
        atform.add_test("to be removed")
        self.generate_old()

        atform.add_test("unchanged")
        self.generate_diff(set())


class TestLabel(DiffBase):
    """Tests for detecting changes to test labels."""

    def test_same(self):
        """Confirm no label changes is not flagged as a difference."""
        atform.add_test("t1", label="label")
        atform.add_test("t2", objective="$label")
        self.generate_old()

        atform.add_test("t1", label="label")
        atform.add_test("t2", objective="$label")
        self.generate_diff(set())

    def test_add_unreferenced(self):
        """Confirm adding an unused label is not flagged as a difference."""
        atform.add_test("title")
        self.generate_old()

        atform.add_test("title", label="label")
        self.generate_diff(set())

    def test_remove_unreferenced(self):
        """Confirm removing an unused label is not flagged as a difference."""
        atform.add_test("title", label="label")
        self.generate_old()

        atform.add_test("title")
        self.generate_diff(set())

    def test_add_placeholder(self):
        """Confirm adding a placeholder to an existing label is detected."""
        atform.add_test("label", label="label")
        atform.add_test("ref", objective="foo")
        self.generate_old()

        atform.add_test("label", label="label")
        atform.add_test("ref", objective="foo $label")
        self.generate_diff({(2,)})

    def test_remove_placeholder(self):
        """Confirm removing a placeholder to an existing label is detected."""
        atform.add_test("label", label="label")
        atform.add_test("ref", objective="foo $label")
        self.generate_old()

        atform.add_test("label", label="label")
        atform.add_test("ref", objective="foo")
        self.generate_diff({(2,)})

    def test_change_label_name(self):
        """Confirm changing the name of a label that points to the same test is not flagged as a difference."""
        atform.add_test("label", label="label1")
        atform.add_test("ref", objective="foo $label1")
        self.generate_old()

        atform.add_test("label", label="label2")
        atform.add_test("ref", objective="foo $label2")
        self.generate_diff(set())

    def test_change_label_test(self):
        """Confirm changing the test referenced by a label is detected."""
        atform.add_test("label1", label="label")
        atform.add_test("ref", objective="foo $label")
        atform.add_test("label2")
        self.generate_old()

        atform.add_test("label1")
        atform.add_test("ref", objective="foo $label")
        atform.add_test("label2", label="label")
        self.generate_diff({(2,)})


class Title(DiffBase):
    """Tests for detecting changes to a test's title."""

    def test_same(self):
        """Confirm no title change is not flagged as a difference."""
        atform.add_test("title")
        self.generate_old()

        atform.add_test("title")
        self.generate_diff(set())

    def test_change(self):
        """Confirm a change to a test's title is detected."""
        atform.add_test("unchanged")
        atform.add_test("old title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("changed title")
        self.generate_diff({(2,)})


class Fields(DiffBase):
    """Tests for detecting changes to a test's user entry fields."""

    def test_same(self):
        """Confirm no field changes is not flagged as a difference."""
        atform.add_field("field", 1, "field")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("field", 1, "field")
        atform.add_test("title")
        self.generate_diff(set())

    def test_add_unused(self):
        """Confirm adding a field that does not appear in any tests is not flagged as a difference."""
        atform.add_test("title")
        self.generate_old()

        atform.add_field("field", 1, "field", active=False)
        atform.add_test("title")
        self.generate_diff(set())

    def test_change_unused(self):
        """Confirm altering a field that does not appear in any tests is not flagged as a difference."""
        atform.add_field("foo", 1, "bar", active=False)
        atform.add_test("title")
        self.generate_old()

        atform.add_field("spam", 5, "eggs", active=False)
        atform.add_test("title")
        self.generate_diff(set())

    def test_remove_unused(self):
        """Confirm removing a field that does not appear in any tests is not flagged as a difference."""
        atform.add_field("field", 1, "field", active=False)
        atform.add_test("title")
        self.generate_old()

        atform.add_test("title")
        self.generate_diff(set())

    def test_add_to_existing(self):
        """Confirm adding a field to an existing set of fields is detected."""
        atform.add_field("field", 1, "field")
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("field", 1, "field")
        atform.add_field("new", 1, "new", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["new"])
        self.generate_diff({(2,)})

    def test_add_to_none(self):
        """Confirm adding a field to a test that previously had none is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("new", 1, "new", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["new"])
        self.generate_diff({(2,)})

    def test_remove_one(self):
        """Confirm removing one field with some still remaining is detected."""
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2")
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2")
        atform.add_test("unchanged")
        atform.add_test("title", exclude_fields=["f2"])
        self.generate_diff({(2,)})

    def test_remove_all(self):
        """Confirm removing all fields is detected."""
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2")
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2")
        atform.add_test("unchanged")
        atform.add_test("title", exclude_fields=["f1", "f2"])
        self.generate_diff({(2,)})

    def test_title(self):
        """Confirm a change to a field's title is detected."""
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["f2"])
        self.generate_old()

        atform.add_field("f1", 1, "f1")
        atform.add_field("diff title", 1, "f2", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["f2"])
        self.generate_diff({(2,)})

    def test_length(self):
        """Confirm a change to a field's length is detected."""
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["f2"])
        self.generate_old()

        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 9, "f2", active=False)
        atform.add_test("unchanged")
        atform.add_test("title", include_fields=["f2"])
        self.generate_diff({(2,)})

    def test_order(self):
        """Confirm changing the order of fields is detected."""
        atform.add_field("f1", 1, "f1")
        atform.add_field("f2", 1, "f2")
        atform.add_test("title")
        self.generate_old()

        atform.add_field("f2", 1, "f2")
        atform.add_field("f1", 1, "f1")
        atform.add_test("title")
        self.generate_diff({(1,)})


class Objective(DiffBase):
    """Tests for detecting changes to a test's objective."""

    def test_same(self):
        """Confirm no objective changes is not flagged as a difference."""
        atform.add_test("title", objective="foo")
        self.generate_old()

        atform.add_test("title", objective="foo")
        self.generate_diff(set())

    def test_add(self):
        """Confirm adding an objective is detected."""
        atform.add_test("unchanged")
        atform.add_test("obj")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("obj", objective="new objective")
        self.generate_diff({(2,)})

    def test_remove(self):
        """Confirm removing an objective is detected."""
        atform.add_test("unchanged")
        atform.add_test("obj", objective="objective")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("obj")
        self.generate_diff({(2,)})

    def test_change(self):
        """Confirm altering an objective is detected."""
        atform.add_test("unchanged")
        atform.add_test("obj", objective="foo")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("obj", objective="bar")
        self.generate_diff({(2,)})


class References(DiffBase):
    """Tests for detecting changes to a test's references."""

    def test_same(self):
        """Confirm no reference changes is not flagged as a difference."""
        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("title", references={"ref1": ["a"], "ref2": ["a"]})
        self.generate_old()

        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("title", references={"ref1": ["a"], "ref2": ["a"]})
        self.generate_diff(set())

    def test_add_category_to_existing(self):
        """Confirm adding a category to an existing set of categories is detected."""
        atform.add_reference_category("ref1", "ref1")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref1": ["a"]})
        self.generate_old()

        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref1": ["a"], "ref2": ["a"]})
        self.generate_diff({(2,)})

    def test_add_category_to_none(self):
        """Confirm adding a category to a test that previously had no references is detected."""
        atform.add_test("unchanged")
        atform.add_test("foo")
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_diff({(2,)})

    def test_add_unused_category(self):
        """Confirm adding an unused category is not detected as a difference."""
        atform.add_test("unchanged")
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        self.generate_diff(set())

    def test_remove_one_category(self):
        """Confirm removing one of many reference categories is detected."""
        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref1": ["a"], "ref2": ["a"]})
        self.generate_old()

        atform.add_reference_category("ref1", "ref1")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref1": ["a"]})
        self.generate_diff({(2,)})

    def test_remove_all_categories(self):
        """Confirm removing all reference categories is detected."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("foo")
        self.generate_diff({(2,)})

    def test_remove_unused_category(self):
        """Confirm removing an unused category is not detected as a difference."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        self.generate_old()

        atform.add_test("unchanged")
        self.generate_diff(set())

    def test_change_title(self):
        """Confirm a change to a category's title is detected."""
        atform.add_reference_category("old title", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_old()

        atform.add_reference_category("new title", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_diff({(2,)})

    def test_add_item(self):
        """Confirm adding a reference item to an existing category is detected."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a", "new"]})
        self.generate_diff({(2,)})

    def test_remove_item(self):
        """Confirm removing a reference item from an existing category is detected."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a", "b"]})
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a"]})
        self.generate_diff({(2,)})

    def test_change_item(self):
        """Confirm changing an existing reference item is detected."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a", "old"]})
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("foo", references={"ref": ["a", "new"]})
        self.generate_diff({(2,)})

    def test_change_category_def_order(self):
        """Confirm changing the category definition order is detected."""
        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref1": ["a"], "ref2": ["x"]})
        self.generate_old()

        atform.add_reference_category("ref2", "ref2")
        atform.add_reference_category("ref1", "ref1")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref1": ["a"], "ref2": ["x"]})
        self.generate_diff({(2,)})

    def test_change_category_key_order(self):
        """Confirm changing the order of category keys is not flagged as a difference."""
        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref1": ["a"], "ref2": ["x"]})
        self.generate_old()

        atform.add_reference_category("ref1", "ref1")
        atform.add_reference_category("ref2", "ref2")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref2": ["x"], "ref1": ["a"]})
        self.generate_diff(set())

    def test_change_item_order(self):
        """Confirm changing the order of reference items is detected."""
        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref": ["r1", "r2"]})
        self.generate_old()

        atform.add_reference_category("ref", "ref")
        atform.add_test("unchanged")
        atform.add_test("title", references={"ref": ["r2", "r1"]})
        self.generate_diff({(2,)})

    def test_change_label(self):
        """Confirm changing a category label only is not flagged as a difference."""
        atform.add_reference_category("ref title", "ref")
        atform.add_test("title", references={"ref": ["a"]})
        self.generate_old()

        atform.add_reference_category("ref title", "newlabel")
        atform.add_test("title", references={"newlabel": ["a"]})
        self.generate_diff(set())


class Equipment(DiffBase):
    """Tests for detecting changes to a test's equipment list."""

    def test_same(self):
        """Confirm no equipment changes is not flagged as a difference."""
        atform.add_test("title", equipment=["foo"])
        self.generate_old()

        atform.add_test("title", equipment=["foo"])
        self.generate_diff(set())

    def test_add_to_none(self):
        """Confirm adding an equipment list to a test that previously had none is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", equipment=["spam"])
        self.generate_diff({(2,)})

    def test_add_to_existing(self):
        """Confirm adding an item to an existing equipment list is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo", "new"])
        self.generate_diff({(2,)})

    def test_remove_all(self):
        """Confirm removing the entire equipment list is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_remove_one(self):
        """Confirm removing a single item while others remain is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo", "bar"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo"])
        self.generate_diff({(2,)})

    def test_change_item(self):
        """Confirm altering an item is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo", "bar"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", equipment=["foo", "spam"])
        self.generate_diff({(2,)})

    def test_change_order(self):
        """Confirm changing item order is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", equipment=["e1", "e2"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", equipment=["e2", "e1"])
        self.generate_diff({(2,)})


class Preconditions(DiffBase):
    """Tests for detecting changes to a test's preconditions."""

    def test_same(self):
        """Confirm no preconditions changes is not flagged as a difference."""
        atform.add_test("title", preconditions=["foo"])
        self.generate_old()

        atform.add_test("title", preconditions=["foo"])
        self.generate_diff(set())

    def test_add_to_none(self):
        """Confirm adding a preconditions list to a test that previously had none is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo"])
        self.generate_diff({(2,)})

    def test_add_to_existing(self):
        """Confirm adding an item to an existing preconditions list is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo", "bar"])
        self.generate_diff({(2,)})

    def test_remove_all(self):
        """Confirm removing the entire preconditions list is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_remove_one(self):
        """Confirm removing a single item while others remain is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo", "bar"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo"])
        self.generate_diff({(2,)})

    def test_change_item(self):
        """Confirm altering an item is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo", "bar"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["foo", "spam"])
        self.generate_diff({(2,)})

    def test_change_order(self):
        """Confirm changing item order is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["p1", "p2"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", preconditions=["p2", "p1"])
        self.generate_diff({(2,)})


class ProcedureList(DiffBase):
    """Tests for detecting changes to a test's overall procedure list."""

    def test_add(self):
        """Confirm adding a procedure is detected."""
        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", procedure=["foo"])
        self.generate_diff({(2,)})

    def test_remove(self):
        """Confirm removing the entire procedure is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title")
        self.generate_diff({(2,)})

    def test_order(self):
        """Confirm changes to step order are detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=["s1", "s2"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", procedure=["s2", "s1"])
        self.generate_diff({(2,)})


class ProcedureText(DiffBase):
    """Tests for detecting changes to procedure step text."""

    def test_same(self):
        """Confirm no text changes is not flagged as a difference."""
        atform.add_test("str", procedure=["step"])
        atform.add_test("dict", procedure=[{"text": "step"}])
        self.generate_old()

        atform.add_test("str", procedure=["step"])
        atform.add_test("dict", procedure=[{"text": "step"}])
        self.generate_diff(set())

    def test_change_type(self):
        """Confirm switching between string and dict with no text changes is not flagged as a difference."""
        atform.add_test("unchanged")
        atform.add_test("str to dict", procedure=["foo"])
        atform.add_test("dict to str", procedure=[{"text": "foo"}])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("str to dict", procedure=[{"text": "foo"}])
        atform.add_test("dict to str", procedure=["foo"])
        self.generate_diff(set())

    def test_change_str_content(self):
        """Confirm changes to string content is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=["foo"])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", procedure=["bar"])
        self.generate_diff({(2,)})

    def test_change_dict_content(self):
        """Confirm changes to dict content is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=[{"text": "foo"}])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", procedure=[{"text": "bar"}])
        self.generate_diff({(2,)})


class ProcedureImage(DiffBase):
    """Tests for detecting changes to the procedure step image."""

    def image_path(self, filename):
        """Generates a path to a procedure step image file."""
        return os.path.join("tests", "images", "procedure", filename)

    def test_same(self):
        """Confirm the same image is not flagged as a difference."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "image": self.image_path("step.png"),
                }
            ],
        )
        self.generate_old()

        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "image": self.image_path("step.png"),
                }
            ],
        )
        self.generate_diff(set())

    def test_add(self):
        """Confirm adding an image is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=[{"text": "foo"}])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "image": self.image_path("step.png"),
                }
            ],
        )
        self.generate_diff({(2,)})

    def test_remove(self):
        """Confirm removing an image is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "image": self.image_path("step.png"),
                }
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("title", procedure=[{"text": "foo"}])
        self.generate_diff({(2,)})

    def test_change(self):
        """Confirm altering an image is detected.

        This is done with mock image content instead of actual files to ensure
        the comparison is applied to the actual image content, not the
        file name, i.e., detecting a change to the image file itself, not its
        path.
        """
        atform.add_test("unchanged")
        with utils.mock_image("JPEG", (10, 10)):
            atform.add_test(
                "title",
                procedure=[{"text": "foo", "image": "spam"}],
            )
        self.generate_old()

        atform.add_test("unchanged")
        with utils.mock_image("JPEG", (20, 20)):
            atform.add_test(
                "title",
                procedure=[{"text": "foo", "image": "spam"}],
            )
        self.generate_diff({(2,)})


class ProcedureField(DiffBase):
    """Tests for detecting changes to procedure step fields."""

    def test_same(self):
        """Confirm no field changes is not flagged as a difference."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step",
                    "fields": [("spam", 1, "eggs"), ("foo", 2, "bar")],
                },
            ],
        )
        self.generate_old()

        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step",
                    "fields": [("spam", 1, "eggs"), ("foo", 2, "bar")],
                },
            ],
        )
        self.generate_diff(set())

    def test_add_to_none(self):
        """Confirm adding a field to a step that previously had none is detected."""
        atform.add_test("unchanged")
        atform.add_test("title", procedure=[{"text": "step"}])
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step",
                    "fields": [("spam", 1, "eggs")],
                }
            ],
        )
        self.generate_diff({(2,)})

    def test_add_to_existing(self):
        """Confirm adding a field to an existing set of fields is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step",
                    "fields": [("spam", 1, "eggs")],
                }
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step",
                    "fields": [("spam", 1, "eggs"), ("foo", 1, "bar")],
                }
            ],
        )
        self.generate_diff({(2,)})

    def test_remove_all(self):
        """Confirm removing all fields from a step is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step"},
            ],
        )
        self.generate_diff({(2,)})

    def test_remove_one(self):
        """Confirm removing one field while others remain is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1), ("eggs", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_diff({(2,)})

    def test_change_title(self):
        """Confirm altering a field title is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("eggs", 1)]},
            ],
        )
        self.generate_diff({(2,)})

    def test_change_width(self):
        """Confirm altering a field width is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 5)]},
            ],
        )
        self.generate_diff({(2,)})

    def test_add_suffix(self):
        """Confirm adding a field suffix is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1, "new")]},
            ],
        )
        self.generate_diff({(2,)})

    def test_remove_suffix(self):
        """Confirm removing a field suffix is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1, "eggs")]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1)]},
            ],
        )
        self.generate_diff({(2,)})

    def test_change_suffix(self):
        """Confirm altering a field suffix is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1, "eggs")]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("spam", 1, "foo")]},
            ],
        )
        self.generate_diff({(2,)})

    def test_change_order(self):
        """Confirm changing the order of fields is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("f1", 1), ("f2", 1)]},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "changes",
            procedure=[
                {"text": "step", "fields": [("f2", 1), ("f1", 1)]},
            ],
        )
        self.generate_diff({(2,)})


class ProcedureLabel(DiffBase):
    """Tests for detecting changes to a procedure step label."""

    def test_same(self):
        """Confirm no label changes is not flagged as a difference."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar $label"},
            ],
        )
        self.generate_old()

        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar $label"},
            ],
        )
        self.generate_diff(set())

    def test_add_unreferenced(self):
        """Confirm adding an unused label is not flagged as a difference."""
        atform.add_test("title", procedure=[{"text": "foo"}])
        self.generate_old()

        atform.add_test("title", procedure=[{"text": "foo", "label": "bar"}])
        self.generate_diff(set())

    def test_remove_unreferenced(self):
        """Confirm removing an unused label is not flagged as a difference."""
        atform.add_test("title", procedure=[{"text": "foo", "label": "bar"}])
        self.generate_old()

        atform.add_test("title", procedure=[{"text": "foo"}])
        self.generate_diff(set())

    def test_add_placeholder(self):
        """Confirm adding a placeholder to an existing label is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar"},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar $label"},
            ],
        )
        self.generate_diff({(2,)})

    def test_remove_placeholder(self):
        """Confirm removing a placeholder to an existing label is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar $label"},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "label",
                },
                {"text": "bar"},
            ],
        )
        self.generate_diff({(2,)})

    def test_change_label_name(self):
        """Confirm changing the name of a label that points to the same step is not flagged as a difference."""
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "labelA",
                },
                {"text": "bar $labelA"},
            ],
        )
        self.generate_old()

        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "foo",
                    "label": "labelB",
                },
                {"text": "bar $labelB"},
            ],
        )
        self.generate_diff(set())

    def test_change_label_step(self):
        """Confirm changing the step referenced by a label is detected."""
        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step 1",
                    "label": "label",
                },
                {
                    "text": "step 2",
                },
                {"text": "step 3 $label"},
            ],
        )
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test(
            "title",
            procedure=[
                {
                    "text": "step 1",
                },
                {
                    "text": "step 2",
                    "label": "label",
                },
                {"text": "step 3 $label"},
            ],
        )
        self.generate_diff({(2,)})


class DiffIdCombination(DiffBase):
    """Tests for combining the diff and ID command line arguments."""

    def test_no_overlap(self):
        """Confirm no tests are built if the given IDs don't contain any tests that changed."""
        atform.add_test("unchanged")
        atform.add_test("will change")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("new title")
        self.generate_diff(set(), id_args="1")

    def test_partial_overlap(self):
        """Confirm correct build if the given IDs contain some of the tests that changed."""
        atform.add_test("unchanged")
        atform.add_test("will change")
        atform.add_test("will change")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("new title")
        atform.add_test("new title")
        self.generate_diff({(3,)}, id_args="3")

    def test_equal(self):
        """Confirm correct build if the given IDs exactly match the tests that changed."""
        atform.add_test("unchanged")
        atform.add_test("will change")
        atform.add_test("will change")
        self.generate_old()

        atform.add_test("unchanged")
        atform.add_test("new title")
        atform.add_test("new title")
        self.generate_diff({(2,), (3,)}, id_args="2-3")
