# Unit tests for the version control interface module.


import atform.vcs
import subprocess
import unittest
from unittest.mock import patch


class NoVersionControl(unittest.TestCase):
    """Unit tests for cases where no version control is available."""

    @patch.object(atform.vcs.Git, 'GIT_CMD', new='this_is_not_git')
    def test_no_git(self):
        """Confirm exception if git is not installed."""
        with self.assertRaises(atform.vcs.NoVersionControlError):
            atform.vcs.Git()

    @patch.object(atform.vcs.Git, '_run_git')
    def test_no_repository(self, mock):
        """Confirm exception if not running in a repository."""
        # Simulate git running outside a repo, which results in a non-zero
        # exit code, and then a CalledProcessError exception.
        mock.side_effect = subprocess.CalledProcessError(-1, 'git')

        with self.assertRaises(atform.vcs.NoVersionControlError):
            atform.vcs.Git()


class Clean(unittest.TestCase):
    """Unit tests for the clean property."""

    @patch.object(atform.vcs.Git, '_run_git')
    def test_uncommitted_changes(self, mock):
        """Confirm clean returns False if uncommitted changes exist."""
        mock.return_value = ' M foo\0?? bar\0' # Non-empty result of git status.
        git = atform.vcs.Git()
        self.assertFalse(git.clean)

    @patch.object(atform.vcs.Git, '_run_git')
    def test_no_uncommitted_changes(self, mock):
        """Confirm clean returns True if no uncommitted changes exist."""
        mock.return_value = '' # Empty result of git status.
        git = atform.vcs.Git()
        self.assertTrue(git.clean)


class Version(unittest.TestCase):
    """Unit tests for the version property."""

    def setUp(self):
        self.git = atform.vcs.Git()

    @patch.object(atform.vcs.Git, '_run_git')
    def test_version(self, mock):
        """Confirm version returns a string containing the HEAD SHA1."""
        mock.return_value = 'spam' # Simulate result of git log.
        self.assertEqual('spam', self.git.version)

    @patch.object(atform.vcs.Git, '_run_git')
    def test_no_commits(self, mock):
        """Confirm version returns None in a repository with no commits.

        This is a special corner case where git log fails; git status is
        unaffected.
        """
        # Simulate failure of git log.
        mock.side_effect = subprocess.CalledProcessError(-1, 'git')

        self.assertIsNone(self.git.version)


class Commands(unittest.TestCase):
    """Unit tests for the actual git commands required for each property.

    These tests use the actual Git class to exercise the underlying commands
    executed for each property. This software resides in a git repository,
    so it is assumed git exists on the system performing unit tests.
    """

    def setUp(self):
        self.git = atform.vcs.Git()

    def test_clean(self):
        """Confirm clean returns a boolean."""
        self.assertIsInstance(self.git.clean, bool)

    def test_version(self):
        """Confirm version returns a string."""
        self.assertIsInstance(self.git.version, str)
