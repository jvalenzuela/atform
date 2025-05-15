# Units tests for the PDF module.


from tests import utils
import atform
import os
import tempfile
import unittest


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
        atform.set_id_depth(2)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=1)
            self.assert_path(root, "1", "1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_single_section_title(self):
        """Confirm path created for an ID with one section with a title."""
        atform.set_id_depth(2)
        atform.section(1, title="spam")
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=1)
            self.assert_path(root, "1 spam", "1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_multi_section_no_title(self):
        """Confirm path created for an ID with multiple sections with no titles."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root, folder_depth=2)
            self.assert_path(root, "1", "1", "1.1.1 foo.pdf")

    @utils.disable_idlock
    @utils.no_args
    def test_multi_section_some_titles(self):
        """Confirm path created for an ID with multiple sections, some with titles."""
        atform.set_id_depth(3)
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
        atform.set_id_depth(3)
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

    ID_DEPTH = 4

    def setUp(self):
        utils.reset()
        atform.set_id_depth(self.ID_DEPTH)
        atform.add_test("Foo")

    @utils.disable_idlock
    @utils.no_args
    def test_default(self):
        """Verify no section folders with the default folder depth."""
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root)
            self.assert_path(root, 0)

    @utils.disable_idlock
    @utils.no_args
    def test_explicit(self):
        """Verify correct section folder depth with explicitly given depths."""
        for depth in range(0, self.ID_DEPTH):
            with self.subTest(depth=depth):
                with tempfile.TemporaryDirectory() as root:
                    atform.generate(path=root, folder_depth=depth)
                    self.assert_path(root, depth)

    def assert_path(self, root, depth):
        """Confirms the output PDF exists in the correct subfolder."""
        path = [root]
        path.extend(["1"] * depth)
        path.append("1.1.1.1 Foo.pdf")
        self.assertTrue(os.path.exists(os.path.join(*path)))
