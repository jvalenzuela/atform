"""Unit tests for the GUI diff tab."""

import unittest
from unittest.mock import patch

import atform
from atform.gui.diff import CompareResult
from .. import utils


@patch(
    "atform.gui.diff.load",
    return_value=CompareResult(changed={(1,)}, new={(2,)}, same={(3,)}),
)
@patch("atform.cache.data", new={"vcs": None})
@patch("atform.gui.buildlist.add")
class AddButtons(unittest.TestCase):
    """Tests for the add to build buttons."""

    def test_changed(self, mock_build, *_mocks):
        """Confirm the changed button adds only changed tests to the build list."""
        widget = atform.gui.diffwidget.Diff(None)
        utils.click_button(widget, "Add Changed Tests To Build")
        mock_build.assert_called_once_with({(1,)})

    def test_new(self, mock_build, *_mocks):
        """Confirm the new button adds only new tests to the build list."""
        widget = atform.gui.diffwidget.Diff(None)
        utils.click_button(widget, "Add New Tests To Build")
        mock_build.assert_called_once_with({(2,)})

    def test_unmodified(self, mock_build, *_mocks):
        """Confirm the unmodified button adds only unmodified tests to the build list."""
        widget = atform.gui.diffwidget.Diff(None)
        utils.click_button(widget, "Add Unmodified Tests To Build")
        mock_build.assert_called_once_with({(3,)})
