"""Unit tests for the ID locking module."""

import contextlib
import io
import os
import pathlib
import unittest
from unittest.mock import mock_open, patch

import atform
from . import utils


def rm_lock_file():
    """Deletes the lock file, if present."""
    try:
        os.remove(atform.idlock.FILENAME)
    except FileNotFoundError:
        pass


class Load(unittest.TestCase):
    """Tests for loading the lock file."""

    def test_no_file(self):
        """Confirm default data is returned if no lock file exists."""
        with patch("atform.idlock.OPEN_LOCK_FILE", side_effect=FileNotFoundError):
            self.assertEqual({}, atform.idlock.load())

    @patch("atform.idlock.OPEN_LOCK_FILE", mock_open(read_data="VERSION,foo\n1,spam"))
    def test_version_mismatch(self):
        """Confirm exception if lock file version doesn't match."""
        with self.assertRaises(atform.idlock.LockFileWarning):
            atform.idlock.verify()

    def test_data(self):
        """Confirm lock file data is correctly parsed."""
        lock_data = f"""VERSION,{atform.version.VERSION}
        42.5,spam
        99.7,eggs"""
        with patch("atform.idlock.OPEN_LOCK_FILE", mock_open(read_data=lock_data)):
            self.assertEqual({(42, 5): "spam", (99, 7): "eggs"}, atform.idlock.load())


class Save(unittest.TestCase):
    """Tests for content saved to the lock file."""

    def setUp(self):
        utils.reset()
        rm_lock_file()

    def get_csv_data(self, mock):
        """Extracts CSV data written to a mock open."""
        rows = []
        for call in mock.mock_calls:
            if call[0].endswith(".write"):
                rows.append(call[1][0].strip().split(","))
        return rows

    @patch("atform.idlock.load", return_value={})
    def test_version(self, *args):
        """Confirm the package version is included in the saved data."""
        atform.add_test("t1")
        with patch("atform.idlock.OPEN_LOCK_FILE", mock_open()) as mock:
            atform.idlock.verify()
        rows = self.get_csv_data(mock)
        self.assertEqual(["VERSION", atform.version.VERSION], rows[0])

    @patch("atform.idlock.load", return_value={})
    def test_id_title(self, *args):
        """Confirm test IDs and titles are saved in ascending order."""
        for i in range(1, 50):
            atform.add_test(f"t{i}")

        with patch("atform.idlock.OPEN_LOCK_FILE", mock_open()) as mock:
            atform.idlock.verify()
        rows = self.get_csv_data(mock)

        for i in range(1, 50):
            self.assertEqual([str(i), f"t{i}"], rows[i])

    @patch("atform.idlock.load", return_value={(1,): "t1"})
    @patch("atform.idlock.OPEN_LOCK_FILE", new_callable=mock_open)
    def test_no_overwrite_current(self, mock_lock_open, *args):
        """Confirm the lock file is not overwritten when the lock file content is current."""
        pathlib.Path(atform.idlock.FILENAME).touch()
        atform.add_test("t1")
        atform.idlock.verify()
        mock_lock_open.assert_not_called()
        rm_lock_file()

    @patch("atform.idlock.load", return_value={})
    @patch("atform.idlock.OPEN_LOCK_FILE", new_callable=mock_open)
    def test_no_overwrite_stale(self, mock_lock_open, *args):
        """Confirm the lock file is not overwritten and an exception if the lock file content is stale."""
        pathlib.Path(atform.idlock.FILENAME).touch()
        atform.add_test("t1")
        with self.assertRaises(atform.idlock.LockFileWarning):
            atform.idlock.verify()
        mock_lock_open.assert_not_called()
        rm_lock_file()

    @utils.no_pdf_output
    @patch("atform.arg.parse", return_value=[(1,)])
    @patch("atform.idlock.load", return_value={})
    def test_no_filter(self, mock_lock_open, *args):
        """Confirm all tests are saved regardless of CLI ID filtering."""
        atform.add_test("t1")
        atform.add_test("t2")  # Excluded by ID filter.
        with patch("atform.idlock.OPEN_LOCK_FILE", mock_open()) as mock:
            atform.generate()
        rows = self.get_csv_data(mock)
        self.assertEqual(["1", "t1"], rows[1])
        self.assertEqual(["2", "t2"], rows[2])
        rm_lock_file()


class ProhibitedChanges(unittest.TestCase):
    """Tests for detecting changes that result in an error."""

    def setUp(self):
        utils.reset()

    def check_changes(self, cm, old_id, old_title, new_id, new_title):
        """Confirm the exception correctly identifies the changed test."""
        diff = cm.exception.diffs[0]
        self.assertEqual(old_id, diff.old_id)
        self.assertEqual(old_title, diff.old_title)
        self.assertEqual(new_id, diff.new_id)
        self.assertEqual(new_title, diff.new_title)

    @patch("atform.idlock.load", return_value={(1,): "t1"})
    def test_insert(self, *args):
        """Confirm exception if a test is shifted due to inserting a new test."""
        atform.add_test("insert")
        atform.add_test("t1")

        with self.assertRaises(atform.idlock.ChangedTestError) as cm:
            atform.idlock.verify()

        self.check_changes(cm, (1,), "t1", (1,), "insert")

    @patch("atform.idlock.load", return_value={(1,): "t1", (2,): "t2"})
    def test_remove(self, *args):
        """Confirm exception if a test is shifted due to removing a test."""
        # t1 deleted
        atform.add_test("t2")

        with self.assertRaises(atform.idlock.ChangedTestError) as cm:
            atform.idlock.verify()

        self.check_changes(cm, (1,), "t1", (1,), "t2")

    @patch("atform.idlock.load", return_value={(1,): "t1"})
    def test_shift_down(self, *args):
        """Confirm exception if a test is moved later without adding any tests."""
        atform.skip_test()
        atform.add_test("t1")

        with self.assertRaises(atform.idlock.ChangedTestError) as cm:
            atform.idlock.verify()

        self.check_changes(cm, (1,), "t1", (2,), "t1")

    @patch("atform.idlock.load", return_value={(2,): "t2"})
    def test_shift_up(self, *args):
        """Confirm exception if a test is moved earlier without removing any other tests."""
        atform.add_test("t2")

        with self.assertRaises(atform.idlock.ChangedTestError) as cm:
            atform.idlock.verify()

        self.check_changes(cm, (2,), "t2", (1,), "t2")

    @patch("atform.idlock.load", return_value={(1,): "t1"})
    def test_id_depth(self, *args):
        """Confirm exception if the ID depth is altered."""
        atform.set_id_depth(2)
        atform.add_test("t1")

        with self.assertRaises(atform.idlock.ChangedTestError) as cm:
            atform.idlock.verify()

        self.check_changes(cm, (1,), "t1", (1, 1), "t1")

    @patch("atform.arg.parse", return_value=[(1,)])
    @patch("atform.idlock.load", return_value={(1,): "t1", (2,): "t2"})
    def test_no_filter(self, *args):
        """Confirm prohibited changes are detected for tests excluded by CLI ID filters."""
        atform.add_test("t1")
        atform.add_test("insert")
        atform.add_test("t2")

        with self.assertRaises(SystemExit):
            atform.generate()


class AllowedChanges(unittest.TestCase):
    """Tests for changes that do not result in an error."""

    def setUp(self):
        utils.reset()

    @patch("atform.idlock.OPEN_LOCK_FILE", mock_open())
    @patch("atform.idlock.load", return_value={(1,): "t1"})
    def test_add(self, *args):
        """Confirm adding a test that does not shift previous tests."""
        atform.add_test("t1")
        atform.add_test("new test")

        atform.idlock.verify()

    @patch("atform.idlock.OPEN_LOCK_FILE", mock_open())
    @patch("atform.idlock.load", return_value={(1,): "t1", (2,): "t2"})
    def test_remove(self, *args):
        """Confirm removing a test that does not shift previous tests."""
        atform.skip_test()  # t1 removed
        atform.add_test("t2")

        atform.idlock.verify()


class Integration(unittest.TestCase):
    """Module integration tests."""

    def setUp(self):
        utils.reset()

    @patch("atform.idlock.verify", side_effect=atform.idlock.ChangedTestError(["foo"]))
    @patch("atform.cache.save")  # Used to determine if generate() created any PDFs.
    def test_inhibit_build(self, mock_cache_save, *args):
        """Confirm an exception from verify() inhibits PDF generation."""
        atform.add_test("t1")
        with self.assertRaises(SystemExit):
            atform.generate()

        # Assume no PDFs were built if the cache was never updated.
        mock_cache_save.assert_not_called()

    @utils.no_pdf_output
    @patch("atform.idlock.verify", side_effect=atform.idlock.LockFileWarning("spam"))
    @patch("atform.cache.save")  # Used to determine if generate() created any PDFs.
    def test_warning_message(self, mock_cache_save, *args):
        """Confirm a warning yields a console message and does not inhibit PDF generation."""
        atform.add_test("t1")
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            atform.generate()
        self.assertEqual("spam", stdout.getvalue().strip())
        mock_cache_save.assert_called_once()
