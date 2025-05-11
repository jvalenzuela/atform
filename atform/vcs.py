"""Version control system interface."""

import shutil
import subprocess


# The current commit SHA1, "draft" if uncommitted changes exist, or None if
# no version control is present.
#
# Pylint message disabled because this is not a constant.
version = None  # pylint: disable=invalid-name


# CLI command name.
GIT_CMD = "git"


def load():
    """Gets the current state from the version control system."""
    global version  # pylint: disable=global-statement
    try:
        path = find_git()
        clean = is_clean(path)
        sha1 = get_sha1(path)
    except NoVersionControlError:
        pass
    else:
        version = sha1 if clean else "draft"


class NoVersionControlError(Exception):
    """Raised when version control information is unavailable.

    This may be due to git not being installed or not running in a
    git repository.
    """


def find_git():
    """Locates the git executable."""
    path = shutil.which(GIT_CMD)
    if not path:
        raise NoVersionControlError()
    return path


def is_clean(path):
    """Determines if the working directory contains uncommitted changes."""
    try:
        status = run_git(
            path,
            "status",
            "--porcelain",
        )

    # Command will fail if this is not a git repository.
    except subprocess.CalledProcessError:
        # This raise is not intended to chain the original exception.
        # pylint: disable=raise-missing-from
        raise NoVersionControlError()

    return status.strip() == ""


def get_sha1(path):
    """Acquires the SHA1 of the current HEAD."""
    try:
        sha1 = run_git(
            path,
            "log",
            "--format=format:%h",
            "-n1",
        )

    # This can fail in a git repo with no commits.
    except subprocess.CalledProcessError:
        sha1 = None

    return sha1


def run_git(path, *args):
    """Executes the git CLI with a given set of arguments."""
    run_args = [path]
    run_args.extend(args)
    result = subprocess.run(
        run_args,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout
