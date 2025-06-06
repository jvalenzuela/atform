"""Unit tests for the cache module."""

import io
import pickle
import unittest
from unittest.mock import patch
from unittest.mock import mock_open

from tests import utils
import atform


class Load(unittest.TestCase):
    """Tests for loading cache data."""

    def setUp(self):
        utils.reset()

    def test_no_file(self):
        """Confirm default data when no cache file exists."""
        with patch("atform.cache.OPEN", new_callable=mock_open) as mock:
            mock.side_effect = OSError
            self.assertEqual(atform.cache.load(), {})

    def test_invalid_file(self):
        """Confirm default data when an invalid file exists."""
        with patch("atform.cache.OPEN", mock_open(read_data=b"spam")):
            self.assertEqual(atform.cache.load(), {})

    def test_version_mismatch(self):
        """Confirm default data when loading a cache file from a different module version."""
        cache = pickle.dumps(
            {
                "version": atform.version.VERSION + "spam",
                "data": {(1,): "foo"},
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=cache)):
            self.assertEqual(atform.cache.load(), {})

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    @patch("atform.cache.load", return_value={})
    def test_load_during_gen(self, mock_load):
        """Confirm cache is loaded during output generation."""
        atform.add_test("a test")
        atform.generate()
        mock_load.assert_called_once_with()


class Save(unittest.TestCase):
    """Tests for saving cache data."""

    def setUp(self):
        utils.reset()

    def test_version(self):
        """Confirm saved data includes the module version."""
        with patch("atform.cache.OPEN", new_callable=mock_open) as mock:
            atform.cache.save({})
        saved = self.get_saved_data(mock)
        self.assertEqual(saved["version"], atform.version.VERSION)

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def test_retain_previous_page_count(self):
        """Confirm page counts from previous tests not built on this run are retained."""
        atform.add_test("t1")

        prev = pickle.dumps(
            {
                "version": atform.version.VERSION,
                "page counts": {(42,): 99},
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=prev)) as mock:
            atform.generate()

        saved = self.get_saved_data(mock)
        self.assertEqual(saved["page counts"][(42,)], 99)

    @utils.no_pdf_output
    @utils.disable_idlock
    @utils.no_args
    def test_overwrite_stale_page_count(self):
        """Confirm page counts for generated tests overwrite page counts from the same tests."""

        atform.add_test("t1")
        atform.add_test("t2")

        stale = pickle.dumps(
            {
                "version": atform.version.VERSION,
                "page counts": {
                    (1,): 10,
                    (2,): 20,
                },
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=stale)) as mock:
            atform.generate()

        saved = self.get_saved_data(mock)
        self.assertEqual(
            saved["page counts"],
            {
                (1,): 1,
                (2,): 1,
            },
        )

    def get_saved_data(self, mock):
        """Retrieves the saved cached data written to a mock open.

        Mock opens will only contain activity related to the cache file
        because open() calls to write PDF content are performed in
        separate processes.
        """
        for call in mock.mock_calls:
            if call[0].endswith("write"):
                return pickle.loads(call[1][0])
