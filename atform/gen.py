"""API to generate output PDFs."""

import concurrent.futures
import sys

from . import arg
from . import cache
from . import idlock
from . import error
from . import pdf
from . import state
from . import vcs


def get_tests_to_build():
    """Assembles the test instances that will be generated.

    Returns a list of test instances matching IDs from command line arguments.
    """
    arg_ids = arg.parse()

    # Default to build all tests if no IDs were selected.
    if not arg_ids:
        return state.tests

    return [t for t in state.tests if id_match_args(t.id, arg_ids)]


def id_match_args(tid, args):
    """Determines if a test ID matches any ID or range from the command line."""
    return next(filter(None, (id_match(tid, arg) for arg in args)), False)


def id_match(tid, target):
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


def submit_tests_to_build(executor, cache_, *build_args):
    """Submits test instances for output generation."""
    futures = []
    for t in get_tests_to_build():
        try:
            test_cache = cache_[t.id]
        except KeyError:
            test_cache = None
        futures.append(executor.submit(pdf.build, t, test_cache, *build_args))
    return futures


def wait_build_complete(futures):
    """Waits for all submitted build jobs to complete."""
    results = {}
    for f in concurrent.futures.as_completed(futures):
        try:
            tid, data = f.result()
        except pdf.BuildError as e:
            print(e)
        else:
            results[tid] = data
    return results


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def generate(*, path="pdf", folder_depth=0):
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`atform.Test`.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

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

    for t in state.tests:
        t.pregenerate()

    if not isinstance(folder_depth, int):
        raise error.UserScriptError(
            "Folder depth must be an integer.",
        )

    max_depth = len(state.current_id) - 1
    if (folder_depth < 0) or (folder_depth > max_depth):
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
        )

    try:
        git = vcs.Git()
    except vcs.NoVersionControlError:
        version = None
    else:
        version = git.version if git.clean else "draft"

    try:
        idlock.verify()
    except idlock.ChangedTestError as e:
        sys.exit(e)
    except idlock.LockFileWarning as e:
        print(e)

    cache_ = cache.load()

    # Use of the ProcessPoolExecutor was based on empirical testing by
    # measuring the amount of time required to generate a large number
    # of mock test documents. The process-based executor yielded a
    # significant improvement, while the thread-based executor was
    # worse than the original, serial implementation.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = submit_tests_to_build(executor, cache_, path, folder_depth, version)
        results = wait_build_complete(futures)

    cache_.update(results)
    cache.save(cache_)
