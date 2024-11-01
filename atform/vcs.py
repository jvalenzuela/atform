# This module contains the version control system interface.


import shutil
import subprocess


class NoVersionControlError(Exception):
    """Raised when version control information is unavailable.

    This may be due to git not being installed or not running in a
    git repository.
    """


class Git:
    """Interface to the git CLI.

    Implemented by running git in subprocess.
    """

    # CLI command name.
    GIT_CMD = "git"

    def __init__(self):
        # Determine if git is installed.
        self.git_path = shutil.which(self.GIT_CMD)
        if not self.git_path:
            raise NoVersionControlError()

        # Execute a benign git command to determine if the current working
        # directory is a repository.
        try:
            self._run_git("status")
        except subprocess.CalledProcessError:
            # This raise is not intended to chain the original exception.
            # pylint: disable=raise-missing-from
            raise NoVersionControlError()

    @property
    def clean(self):
        """Determines if the working directory contains uncommitted changes."""
        status = self._run_git(
            "status",
            "--porcelain",
        )
        return status.strip() == ""

    @property
    def version(self):
        """Acquires the SHA1 of the current HEAD."""
        try:
            sha1 = self._run_git(
                "log",
                "--format=format:%h",
                "-n1",
            )

        # This can fail in a git repo with no commits.
        except subprocess.CalledProcessError:
            sha1 = None

        return sha1

    def _run_git(self, *args):
        """Executes the git CLI with a given set of arguments."""
        run_args = [self.git_path]
        run_args.extend(args)
        result = subprocess.run(
            run_args,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout
