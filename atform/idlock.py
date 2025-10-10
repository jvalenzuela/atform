"""Test ID/title lock file implementation.

This module implements a system to help prevent inadvertent shifts in test
numbering. Test IDs and titles are written to an external lock file, which
is loaded each run and compared to the current tests.
"""

import csv
from dataclasses import dataclass
import functools
import itertools
import os
import textwrap
from typing_extensions import Self

from . import id as id_
from . import state
from . import version


# True if the lock file matches the current test content; set by verify()
# after comparing the existing test content to the lock file.
lockfile_current = False  # pylint: disable=invalid-name


# Lock file name.
FILENAME = "id.csv"


IdTitleMapType = dict[id_.IdType, str]


def wrap(s: str) -> str:
    """Line wraps string."""
    return textwrap.fill(textwrap.dedent(s))


class ChangedTestError(Exception):
    """Raised if any unintentional changes were found."""

    def __init___(self, diffs: list[ChangedTest]) -> None:
        super().__init__()
        self.diffs = diffs

    def __str__(self) -> str:
        lines = [
            wrap(
                f"""\
                Possible unintentional change to {len(self.diffs)} test(s);
                no PDFs were generated. The first difference is:
                """
            ),
            "",
            str(self.diffs[0]),
            "",
            wrap(
                f"""\
                If this is intentional delete {FILENAME} run the script again,
                otherwise the changes must be reverted before PDFs can
                be generated.
                """
            ),
        ]
        return "\n".join(lines)


class LockFileWarning(Exception):
    """Raised if a non-fatal problem was encountered."""

    def __str__(self) -> str:
        return wrap(self.args[0])


@dataclass(repr=False)
@functools.total_ordering
class ChangedTest:
    """Storage for a test that has changed relative to the lock file."""

    old_id: tuple
    old_title: str
    new_id: tuple
    new_title: str

    def __str__(self) -> str:
        old_id_str = id_.to_string(self.old_id)
        new_id_str = id_.to_string(self.new_id)
        return f"{old_id_str} {self.old_title} -> {new_id_str} {self.new_title}"

    # Ignore incompatible overrides for the other parameter as this
    # method shall only be used to compare ChangedTest objects.
    def __eq__(self, other: Self) -> bool:  # type: ignore[override]
        return self.new_id == other.new_id

    # Ignore incompatible overrides for the other parameter as this
    # method shall only be used to compare ChangedTest objects.
    def __lt__(self, other: Self) -> bool:  # type: ignore[override]
        return self.new_id < other.new_id


# Capture common arguments to open() when used for CSV operations, and also
# provides an attribute for unit tests to patch open() only in this module.
OPEN_LOCK_FILE = functools.partial(open, FILENAME, newline="", encoding="utf8")


def verify() -> None:
    """Top-level function to execute the entire verification process."""
    global lockfile_current  # pylint: disable=global-statement
    current_tests = {t.id: t.title for t in state.tests.values()}
    old_tests = load()
    compare(current_tests, old_tests)
    save(current_tests, old_tests)

    # The lock file can now be considered current if no exceptions have been
    # raised.
    lockfile_current = True


def load() -> IdTitleMapType:
    """Loads test information from the lock file."""
    tests = {}
    check_version = True
    try:
        with OPEN_LOCK_FILE() as f:
            reader = csv.reader(f)
            for row in reader:
                # Verify matching module version in the first row.
                if check_version:
                    if row[1] != version.VERSION:
                        raise LockFileWarning(
                            f"""\
                            The ID lock file version does not match the
                            current atform version. Delete {FILENAME} and run
                            the script again to regenerate the ID lock file
                            with the currently installed version.
                            """
                        )
                    check_version = False

                else:
                    tid = tuple(int(i) for i in row[0].split("."))
                    title = row[1]
                    tests[tid] = title

    # Yield an empty data set if no lock file exists.
    except FileNotFoundError:
        pass

    except OSError as e:
        raise LockFileWarning(f"Error reading ID lock file: {e}") from e

    except (csv.Error, IndexError, ValueError) as e:
        raise LockFileWarning(
            f"""\
            The ID lock file is corrupt. Delete {FILENAME} and run the
            script again to regenerate the ID lock file.
            """
        ) from e

    return tests


def compare(current_tests: IdTitleMapType, old_tests: IdTitleMapType) -> None:
    """Compares the current tests with those from the lock file."""
    diffs = check_titles(old_tests)
    diffs.extend(check_ids(current_tests, old_tests))
    if diffs:
        diffs.sort()
        raise ChangedTestError(diffs)


def check_titles(old: IdTitleMapType) -> list[ChangedTest]:
    """Checks for tests that have changed titles.

    The intent is to detect title changes in existing tests, i.e., the
    same ID between the current and old tests, but with a different title.
    """
    diffs = []
    for test in state.tests.values():
        try:
            old_title = old[test.id]

        except KeyError:
            pass

        else:
            if test.title != old_title:
                diffs.append(ChangedTest(test.id, old_title, test.id, test.title))

    return diffs


def check_ids(
    current_tests: IdTitleMapType, old_tests: IdTitleMapType
) -> list[ChangedTest]:
    """Checks for tests with identical titles but different IDs.

    The intent is to detect tests that have been inadvertently shifted by
    the addition of new tests and the original ID of the shifted test
    is no longer used.
    """
    # IDs that do not exist in the lock file are considered new tests.
    new_ids = set(current_tests).difference(old_tests)

    # IDs that exist only in the lock file are considered removed.
    removed_ids = set(old_tests).difference(current_tests)

    diffs = []

    for new_id, rem_id in itertools.product(new_ids, removed_ids):
        new_title = current_tests[new_id]
        rem_title = old_tests[rem_id]

        # The test is considered changed if its current title matches the
        # title of a removed test.
        if new_title == rem_title:
            diffs.append(ChangedTest(rem_id, rem_title, new_id, new_title))

    return diffs


def save(current_tests: IdTitleMapType, old_tests: IdTitleMapType) -> None:
    """Stores the current tests to the lock file."""
    # Do not overwrite an existing lock file, ensuring the lock file is only
    # updated when the user explicitly allows it by first deleting the
    # existing file.
    if os.path.exists(FILENAME):
        if current_tests != old_tests:
            raise LockFileWarning(
                f"""\
                The ID lock file needs to be updated to reflect the current
                set of tests. Delete {FILENAME} and run the script again to
                update the ID lock file with the current test information.
                """
            )
        return

    try:
        with OPEN_LOCK_FILE("w") as f:
            writer = csv.writer(f)
            writer.writerow(["VERSION", version.VERSION])
            rows = [
                [id_.to_string(tid), current_tests[tid]]
                for tid in sorted(current_tests)
            ]
            writer.writerows(rows)
    except OSError as e:
        raise LockFileWarning(f"Error writing ID lock file: {e}") from e
