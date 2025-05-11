"""Unit tests for the build() function initiating the PDF build process."""

import unittest
from unittest.mock import patch

import atform


@patch("atform.gui.build.Dialog")
@patch("atform.parallelbuild.Builder")
class Build(unittest.TestCase):
    """build() function unit tests."""

    def test_submit_tests(self, mock_builder, _mock_dialog):
        """Confirm all IDs are submitted for building."""
        ids = range(3)
        path = "foo"
        folder_depth = 42
        atform.gui.build.build(ids, path, folder_depth)
        submit_calls = mock_builder().__enter__().submit_test.call_args_list
        self.assertEqual(len(ids), len(submit_calls))
        for i in ids:
            args, _kwargs = submit_calls[i]
            self.assertEqual(i, args[0])
            self.assertEqual(path, args[1])
            self.assertEqual(folder_depth, args[2])

    def test_callback(self, mock_builder, mock_dialog):
        """Confirm future callbacks queue the correct test ID."""
        ids = range(3)
        atform.gui.build.build(ids, "foo", 0)
        q = mock_dialog.call_args[0][2]

        # Extract the lambda callbacks assigned to each future.
        add_done_callbacks = (
            mock_builder().__enter__().submit_test().add_done_callback.call_args_list
        )
        cb = [args[0] for args, kwargs in add_done_callbacks]

        self.assertEqual(len(ids), len(cb))
        for i in ids:
            self.assertTrue(q.empty())  # Queue is intially empty.
            cb[i](None)  # Execute callback; future argument is unused.
            self.assertEqual(i, q.get(block=True))  # Correct queued ID.
            self.assertTrue(q.empty())  # No further queue content.

    def test_dialog(self, _mock_builder, mock_dialog):
        """Confirm the GUI dialog is launched."""
        atform.gui.build.build([], "", 0)
        mock_dialog.assert_called_once()
