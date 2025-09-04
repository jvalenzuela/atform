"""Unit tests for the BuildList panel."""

import unittest
from unittest.mock import patch

import atform
from .. import utils


def click_build():
    """Simulates clicking the build button."""
    utils.click_button(atform.gui.buildlist.BuildList.instance, "Build PDFs")


class Add(unittest.TestCase):
    """Tests for the add() function."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")
        self.buildlist = atform.gui.buildlist.BuildList(None, None, None)

    def test_add(self):
        """Confirm tests are added to the test list."""
        atform.gui.buildlist.add({(1,), (2,)})
        self.assertEqual({(1,), (2,)}, self.buildlist.testlist.all_tests)


class RemoveButton(unittest.TestCase):
    """Tests for the remove selected button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")

    def test_remove_some(self):
        """Confirm removal when some tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,))
        self.click()
        self.assert_remaining_tests({(2,)})

    def test_remove_all(self):
        """Confirm removal when all tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,), (2,))
        self.click()
        self.assert_remaining_tests(set())

    def test_remove_none(self):
        """Confirm no change when no tests are selected."""
        atform.gui.buildlist.BuildList(None, None, None)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set()
        self.click()
        self.assert_remaining_tests({(1,), (2,)})

    def click(self):
        """Simulates clicking the remove button."""
        utils.click_button(atform.gui.buildlist.BuildList.instance, "Remove Selected")

    def assert_remaining_tests(self, expected):
        """Confirms the test list contains the expected set of tests."""
        actual = atform.gui.buildlist.BuildList.instance.testlist.all_tests
        self.assertEqual(expected, actual)


class Path(unittest.TestCase):
    """Tests for the output path entry."""

    def setUp(self):
        utils.reset()
        atform.add_test("a test")
        atform.gui.buildlist.BuildList(None, "spam", 0)
        atform.gui.buildlist.add({(1,)})
        self.entry = utils.find_widget_by_class(
            atform.gui.buildlist.BuildList.instance, "Entry"
        )

    def test_initialize(self):
        """Confirm path is initialized with the BuildList parameter."""
        self.assertEqual("spam", self.entry.get())

    @patch("atform.gui.buildlist.filedialog.askdirectory")
    def test_select(self, mock_dialog):
        """Confirm selecting a new folder changes the current path."""
        mock_dialog.return_value = "foo"
        self.click_select()
        self.assertEqual("foo", self.entry.get())

    @patch("atform.gui.buildlist.filedialog.askdirectory")
    def test_cancel(self, mock_dialog):
        """Confirm cancelling the folder selection dialog leaves the path unaffected."""
        mock_dialog.return_value = None
        self.click_select()
        self.assertEqual("spam", self.entry.get())

    @patch("atform.gui.buildlist.filedialog.askdirectory")
    @patch("atform.gui.build.build")
    def test_build_parameter(self, mock_build, mock_dialog):
        """Confirm current path is passed to the builder."""
        # Simulate selecting something other than the default value.
        mock_dialog.return_value = "foo"
        self.click_select()

        click_build()
        mock_build.assert_called_with({(1,)}, "foo", 0)

    def click_select(self):
        """Simulates clicking the button to open the folder selection dialog."""
        utils.click_button(atform.gui.buildlist.BuildList.instance, "...")


class FolderDepth(unittest.TestCase):
    """Tests for the folder depth control."""

    def setUp(self):
        utils.reset()

    def test_initialize(self):
        """Confirm depth is initialized with the BuildList parameter."""
        atform.set_id_depth(3)
        atform.gui.buildlist.BuildList(None, "spam", 2)
        spin = self.get_widget()
        self.assertEqual(2, int(spin.get()))

    def test_readonly(self):
        """Confirm direct entry is prohibited."""
        spin = self.get_widget()
        self.assertEqual("readonly", spin.cget("state"))

    def test_range_single_level(self):
        """Confirm allowable range when ID depth is one."""
        atform.gui.buildlist.BuildList(None, "spam", 0)
        spin = self.get_widget()
        self.assertEqual(0, int(spin.cget("from")))
        self.assertEqual(0, int(spin.cget("to")))

    def test_range_multiple_level(self):
        """Confirm allowable range when ID depth is greater than one."""
        atform.set_id_depth(3)
        atform.gui.buildlist.BuildList(None, "spam", 0)
        spin = self.get_widget()
        self.assertEqual(0, int(spin.cget("from")))
        self.assertEqual(2, int(spin.cget("to")))

    @patch("atform.gui.build.build")
    def test_build_parameter(self, mock_build):
        """Confirm current value is passed to the builder."""
        atform.set_id_depth(3)
        atform.add_test("foo")
        atform.gui.buildlist.BuildList(None, "spam", 2)
        atform.gui.buildlist.add({(1, 1, 1)})

        # Click the down button to shift off the default value.
        spin = self.get_widget()
        spin.invoke("buttondown")

        click_build()
        mock_build.assert_called_with({(1, 1, 1)}, "spam", 1)

    def get_widget(self):
        """Finds the spin box widget."""
        return utils.find_widget_by_class(
            atform.gui.buildlist.BuildList.instance,
            "Spinbox",
        )


@patch("atform.gui.build.build")
class BuildButton(unittest.TestCase):
    """Tests for the build button."""

    def setUp(self):
        utils.reset()
        atform.add_test("foo")
        atform.add_test("bar")

    def test_none_selected(self, mock_build):
        """Confirm all tests are built when none are selected."""
        atform.gui.buildlist.BuildList(None, "path", 0)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set()
        click_build()
        mock_build.assert_called_once_with({(1,), (2,)}, "path", 0)

    def test_some_selected(self, mock_build):
        """Confirm all tests are built when some are selected."""
        atform.gui.buildlist.BuildList(None, "path", 0)
        atform.gui.buildlist.add({(1,), (2,)})
        atform.gui.buildlist.BuildList.instance.testlist.tree.selection_set((1,))
        click_build()
        mock_build.assert_called_once_with({(1,), (2,)}, "path", 0)

    def test_empty(self, mock_build):
        """Confirm nothing is built if the list is empty."""
        atform.gui.buildlist.BuildList(None, "path", 0)
        click_build()
        mock_build.assert_not_called()

    def test_clear_after(self, _mock_build):
        """Confirm listing is cleared after building."""
        atform.gui.buildlist.BuildList(None, "path", 0)
        atform.gui.buildlist.add({(1,), (2,)})
        click_build()
        self.assertEqual(
            set(), atform.gui.buildlist.BuildList.instance.testlist.all_tests
        )
