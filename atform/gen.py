"""API to generate output PDFs."""

import argparse
import concurrent.futures
import sys
from typing import Union

from . import addtest
from . import arg
from . import cache
from . import id as id_
from . import idlock
from . import error
from . import misc
from . import parallelbuild
from . import pdf
from . import vcs
from . import gui


def get_tests_to_build(args: argparse.Namespace) -> set[id_.IdType]:
    """Assembles the test instances that will be generated.

    Returns a set of test IDs selected from command line arguments.
    """
    ids = set(addtest.tests.keys())

    if args.id:
        ids.intersection_update(
            tid for tid in addtest.tests if id_match_args(tid, args.id)
        )

    return ids


def id_match_args(
    tid: id_.IdType, args: list[Union[id_.IdType, id_.IdRangeType]]
) -> bool:
    """Determines if a test ID matches any ID or range from the command line."""
    return next(filter(None, (id_match(tid, arg) for arg in args)), False)


def id_match(tid: id_.IdType, target: Union[id_.IdType, id_.IdRangeType]) -> bool:
    """Determines if a test ID matches a single ID from the command line.

    Comparison between the test and target ID(s) only evaluates the number of
    target fields, allowing short IDs representing a section to match all
    tests within that section, e.g, 4.2 will match 4.2.x because only the
    first two fields are tested.
    """
    if isinstance(target[0], int):  # Target is a single ID.
        return tid[: len(target)] == target

    # Otherwise target is a range.
    start, end = target
    return (start <= tid[: len(start)]) and (end >= tid[: len(end)])


def cli_build(path: str, folder_depth: int, args: argparse.Namespace) -> None:
    """Builds tests for CLI operation."""
    with parallelbuild.Builder() as builder:
        ids = get_tests_to_build(args)
        futures = [builder.submit_test(tid, path, folder_depth) for tid in ids]
        for f in concurrent.futures.as_completed(futures):
            try:
                builder.process_result(f)
            except pdf.BuildError as e:
                print(e, file=sys.stderr)


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def generate(*, path: str = "pdf", folder_depth: int = 0) -> None:
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`atform.Test`. Calling this function *must*
    be dependent on an ``if __name__ == "__main__":`` condition.
    Furthermore, if the project is organized into multiple scripts, this
    function can only be called from the top-level script.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

    If enabled via the :ref:`command line option <cli_gui>`, the GUI will
    be started automatically by this function, and the specific PDFs generated
    will be determined by user interaction with the GUI. If the GUI is
    launched, this function will not return until the GUI is closed.

    Args:
        path (str, optional): Output directory where PDFs will be saved,
            relative to the location where the top-level script resides.
        folder_depth (int, optional): The number of test ID levels used to
            create section folders. For example, if ``folder_depth`` is 2,
            all PDFs will be output into section subfolders two deep,
            such as :file:`1/2/1.2.3.4 Test.pdf`.

            Must be greater than or equal to 0, and less than the ID
            depth set with :py:func:`atform.set_id_depth`.
    """
    if not isinstance(path, str):
        raise error.UserScriptError(
            "Output path must be a string.",
        )

    for t in addtest.tests.values():
        t.pregenerate()

    if not isinstance(folder_depth, int):
        raise error.UserScriptError(
            "Folder depth must be an integer.",
        )

    try:
        misc.validate_folder_depth(folder_depth)
    except ValueError as e:
        max_depth = misc.max_folder_depth()
        if max_depth:
            remedy = f"""
            The folder depth must be within 0 and {max_depth}, inclusive.
            """
        else:
            remedy = """
            atform.set_id_depth() must first be called to increase the
            number of test identifier fields before folder_depth can
            be increased beyond zero.
            """
        raise error.UserScriptError(
            "Invalid folder depth value.",
            remedy,
        ) from e

    args = arg.parse()
    vcs.load()

    try:
        idlock.verify()
    except idlock.ChangedTestError as e:
        sys.exit(str(e))
    except idlock.LockFileWarning as e:
        print(e)

    cache.load()

    if args.gui:
        gui.run(path, folder_depth)
    else:
        cli_build(path, folder_depth, args)

    cache.save()
