# Units tests for the PDF module.


from tests import utils
import atform
import os
import tempfile
import unittest
from unittest.mock import patch


class SectionTitles(unittest.TestCase):
    """Unit tests for translating section titles to paths."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    @utils.no_args
    def test_no_section(self):
        """Confirm path created for a single-level ID."""
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root)
            self.assert_path(root, "1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_single_section_no_title(self):
        """Confirm path created for an ID with one section and no title."""
        atform.section(1)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=1)
            self.assert_path(root, "1", "1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_single_section_title(self):
        """Confirm path created for an ID with one section with a title."""
        atform.section(1, title="spam")
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=1)
            self.assert_path(root, "1 spam", "1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_multi_section_no_title(self):
        """Confirm path created for an ID with multiple sections with no titles."""
        atform.section(2)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=2)
            self.assert_path(root, "1", "1", "1.1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_multi_section_some_titles(self):
        """Confirm path created for an ID with multiple sections, some with titles."""
        atform.section(1)
        atform.section(2, title="spam")
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=2)
            self.assert_path(root, "1", "1 spam", "1.1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_multi_section_all_titles(self):
        """Confirm path created for an ID with multiple sections, all with titles."""
        atform.section(1, title="spam")
        atform.section(2, title="eggs")
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=2)
            self.assert_path(root, "1 spam", "1 eggs", "1.1.1 foo.pdf")

    def assert_path(self, *paths):
        """Asserts a given path exists."""
        target = os.path.join(*paths)
        exists = os.path.exists(target)
        self.assertTrue(exists, msg=os.path.join(*paths[1:]))


class OutputSectionPathDepth(unittest.TestCase):
    """Tests for output section folder depth."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    @utils.no_args
    def test_no_section_default_depth(self):
        """Verify correct path with no sections and default folder depth."""
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root)
            self.assert_path(root, "1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_no_section_nonzero_depth(self):
        """Verify correct path with no sections and nonzero folder depth."""
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=42)
            self.assert_path(root, "1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_section_default_depth(self):
        """Verify correct path with sections and default folder depth."""
        atform.section(1)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root)
            self.assert_path(root, "1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_depth_less_than_section(self):
        """Verify correct path when folder depth is less than section depth."""
        atform.section(2)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=1)
            self.assert_path(root, "1", "1.1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_depth_equal_section(self):
        """Verify correct path when folder depth equals section depth."""
        atform.section(2)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=2)
            self.assert_path(root, "1", "1", "1.1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_depth_greater_section(self):
        """Verify correct path when folder depth exceeds section depth."""
        atform.section(2)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=42)
            self.assert_path(root, "1", "1", "1.1.1 foo.pdf")

    def assert_path(self, *path):
        """Confirms the output PDF exists in the correct subfolder."""
        self.assertTrue(os.path.exists(os.path.join(*path)))


class BuildError(unittest.TestCase):
    """Tests for errors during the build process."""

    def setUp(self):
        utils.reset()

    @patch("atform.pdf.doc.TestDocument", side_effect=KeyError("spam"))
    def test_exception(self, _mock):
        """Confirm exceptions during building raise a BuildError."""
        atform.add_test("foo")
        test = utils.get_test_content()
        with self.assertRaises(atform.pdf.doc.BuildError) as cm:
            atform.pdf.doc.build(test, 1, "")
        msg = str(cm.exception)
        self.assertIn(test.full_name, msg)
        self.assertIn("spam", msg)
