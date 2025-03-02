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
            atform.cache.load()
        self.assertIsNone(atform.cache.get_test_data((1,)))

    def test_invalid_file(self):
        """Confirm default data when an invalid file exists."""
        with patch("atform.cache.OPEN", mock_open(read_data=b"spam")):
            atform.cache.load()
        self.assertIsNone(atform.cache.get_test_data((1,)))

    def test_version_mismatch(self):
        """Confirm default data when loading a cache file from a different module version."""
        cache = pickle.dumps(
            {
                "version": atform.version.VERSION + "spam",
                "tests": {(1,): "foo"},
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=cache)):
            atform.cache.load()
        self.assertIsNone(atform.cache.get_test_data((1,)))

    def test_load(self):
        """Confirm cache is loaded during output generation."""
        atform.add_test("a test")
        cache = pickle.dumps(
            {
                "version": atform.version.VERSION,
                "tests": {(42, 99): {"page count": 123}},
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=cache)):
            atform.generate()
        self.assertEqual(atform.cache.get_test_data((42, 99)), {"page count": 123})


class Save(unittest.TestCase):
    """Tests for saving cache data."""

    def setUp(self):
        utils.reset()

    def test_version(self):
        """Confirm saved data includes the module version."""
        atform.add_test("t1")
        with patch("atform.cache.OPEN", new_callable=mock_open) as mock:
            atform.generate()
        saved = self.get_saved_data(mock)
        self.assertEqual(saved["version"], atform.version.VERSION)

    def test_overwrite_stale_data(self):
        """Confirm saved data overwrites previously-cached data."""

        atform.add_test("t1")
        atform.add_test("t2")

        stale = pickle.dumps(
            {
                "version": atform.version.VERSION,
                "tests": {
                    (42, 1): {"page count": 10},
                    (42, 2): {"page count": 20},
                },
            }
        )
        with patch("atform.cache.OPEN", mock_open(read_data=stale)) as mock:
            atform.generate()

        saved = self.get_saved_data(mock)
        self.assertEqual(
            saved["tests"],
            {
                (1,): {"page count": 1},
                (2,): {"page count": 1},
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
