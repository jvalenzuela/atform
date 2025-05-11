# Unit tests for the version control interface module.


import atform
import subprocess
import unittest
from unittest.mock import patch

from tests import utils


class NoVersionControl(unittest.TestCase):
    """Unit tests for cases where no version control is available."""

    def setUp(self):
        utils.reset()

    @patch.object(atform.vcs, "GIT_CMD", new="this_is_not_git")
    def test_no_git(self):
        """Confirm no version if git is not installed."""
        atform.vcs.load()
        self.assertIsNone(atform.vcs.version)

    @patch("atform.vcs.run_git")
    def test_no_repository(self, mock):
        """Confirm no version if not running in a repository."""
        # Simulate git running outside a repo, which results in a non-zero
        # exit code, and then a CalledProcessError exception.
        mock.side_effect = subprocess.CalledProcessError(-1, "git")

        atform.vcs.load()
        self.assertIsNone(atform.vcs.version)


class Version(unittest.TestCase):
    """Tests for the current version resulting from various git states."""

    def setUp(self):
        utils.reset()

    @patch("atform.vcs.run_git")
    def test_uncommitted_changes(self, mock):
        """Confirm draft if uncommitted changes exist."""

        def mock_run(path, *args):
            if args[0] == "status":
                return " M foo\0?? bar\0"
            return "sha1"

        mock.side_effect = mock_run

        atform.vcs.load()
        self.assertEqual("draft", atform.vcs.version)

    @patch("atform.vcs.run_git")
    def test_no_uncommitted_changes(self, mock):
        """Confirm non-draft no uncommitted changes exist."""

        def mock_run(path, *args):
            if args[0] == "log":
                return "sha1"
            return ""

        mock.side_effect = mock_run

        atform.vcs.load()
        self.assertEqual("sha1", atform.vcs.version)

    @patch("atform.vcs.run_git")
    def test_no_commits(self, mock):
        """Confirm no version in a repository with no commits.

        This is a special corner case where git log fails; git status is
        unaffected.
        """

        def mock_run(path, *args):
            if args[0] == "log":
                raise subprocess.CalledProcessError(-1, "git")
            return ""

        mock.side_effect = mock_run

        atform.vcs.load()
        self.assertIsNone(atform.vcs.version)


class Integration(unittest.TestCase):
    """Module integration tests"""

    def setUp(self):
        utils.reset()

    @utils.no_args
    @utils.no_pdf_output
    @utils.disable_idlock
    @patch("atform.vcs.load")
    def test_load_call(self, mock_load):
        """Confirm version is loaded upon generate()."""
        atform.add_test("foo")
        atform.generate()
        mock_load.assert_called_once()


class Commands(unittest.TestCase):
    """Unit tests for the actual git commands.

    This software resides in a git repository, so it is assumed git exists
    on the system performing unit tests.
    """

    def setUp(self):
        self.path = atform.vcs.find_git()

    def test_clean(self):
        """Confirm clean returns a boolean."""
        self.assertIsInstance(atform.vcs.is_clean(self.path), bool)

    def test_sha1(self):
        """Confirm sha1 returns a string."""
        self.assertIsInstance(atform.vcs.get_sha1(self.path), str)
