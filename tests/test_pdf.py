# Units tests for the PDF module.


from tests import utils
import atform.pdf
import os
import tempfile
import unittest


class BuildPath(unittest.TestCase):
    """Unit tests for the build_path() function."""

    def setUp(self):
        utils.reset()

    def test_no_section(self):
        """Confirm path created for a single-level ID."""
        self.assertEqual("root", atform.pdf.doc.build_path((42,), "root", 0))

    def test_single_section_no_title(self):
        """Confirm path created for an ID with one section and no title."""
        self.assertEqual(
            os.path.join("root", "42"), atform.pdf.doc.build_path((42, 1), "root", 1)
        )

    def test_single_section_title(self):
        """Confirm path created for an ID with one section with a title."""
        atform.state.section_titles[(42,)] = "Spam"
        self.assertEqual(
            os.path.join("root", "42 Spam"),
            atform.pdf.doc.build_path((42, 1), "root", 1),
        )

    def test_multi_section_no_title(self):
        """Confirm path created for an ID with multiple sections with titles."""
        self.assertEqual(
            os.path.join("root", "42", "99"),
            atform.pdf.doc.build_path((42, 99, 1), "root", 2),
        )

    def test_multi_section_some_titles(self):
        """Confirm path created for an ID with multiple sections, some with titles."""
        atform.state.section_titles[(42, 99)] = "Spam"
        self.assertEqual(
            os.path.join("root", "42", "99 Spam"),
            atform.pdf.doc.build_path((42, 99, 1), "root", 2),
        )

    def test_multi_section_all_titles(self):
        """Confirm path created for an ID with multiple sections, all with titles."""
        atform.state.section_titles[(42,)] = "Foo"
        atform.state.section_titles[(42, 99)] = "Bar"
        self.assertEqual(
            os.path.join("root", "42 Foo", "99 Bar"),
            atform.pdf.doc.build_path((42, 99, 1), "root", 2),
        )


class OutputSectionPathDepth(unittest.TestCase):
    """Tests for output section folder depth."""

    ID_DEPTH = 4

    def setUp(self):
        utils.reset()
        atform.set_id_depth(self.ID_DEPTH)
        atform.add_test("Foo")

    @utils.disable_idlock
    def test_default(self):
        """Verify no section folders with the default folder depth."""
        with tempfile.TemporaryDirectory() as root:
            atform.generate(path=root)
            self.assert_path(root, 0)

    @utils.disable_idlock
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
