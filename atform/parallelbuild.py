"""
This module implements building output PDFs in parallel via multiprocessing.
"""

import concurrent.futures
import datetime
import getpass
import os

from . import cache
from . import pdf
from . import state
from . import vcs


class Builder(concurrent.futures.ProcessPoolExecutor):
    """Context manager for building test PDFs.

    Use of the ProcessPoolExecutor was based on empirical testing by
    measuring the amount of time required to generate a large number
    of mock test documents. The process-based executor yielded a
    significant improvement, while the thread-based executor was
    worse than the original, serial implementation.
    """

    # Value passed to the superclass's __init__(). Under normal operation
    # this is the same as the default value, so it has no effect. It is
    # changed during unit testing to minimize the number of processes
    # created, accelerating unit test execution as no unit test requires
    # more than one worker process.
    MAX_WORKERS = None

    def __init__(self):
        super().__init__(
            initializer=pdf.init,
            initargs=self._worker_init_data,
            max_workers=self.MAX_WORKERS,
        )

        # Ensure the cache has a page count storage area.
        try:
            cache.data["page counts"]
        except KeyError:
            cache.data["page counts"] = {}

        self.page_counts = cache.data["page counts"]

    @property
    def _worker_init_data(self):
        """Assembles arguments for the worker initializer."""
        data = {
            "images": state.images,
            "timestamp": datetime.datetime.today(),
            "version": vcs.version,
        }

        try:
            user = getpass.getuser()

        # Broad exception class used because documentation states Python
        # versions < 3.13 may raise various undocumented exceptions besides
        # OSError.
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        else:
            data["user"] = user

        return (data,)

    def submit_test(self, tid, root, folder_depth):
        """Schedules a test for building."""
        try:
            pages = self.page_counts[tid]
        except KeyError:
            pages = 1

        test = state.tests[tid]
        path = build_path(test.id, root, folder_depth)
        return self.submit(pdf.build, test, pages, path)

    def process_result(self, future):
        """Handles the result of building a single PDF."""
        result = future.result()
        self.page_counts.update(result)


def build_path(tid, root, depth):
    """Constructs a path where a test's output PDF will be written.

    The path will consist of the root, followed by a folder per
    section number limited to depth, e.g., <root>/<x>/<y> for an ID x.y.z
    and depth 2. The final number in an ID is not translated to a folder.
    """
    folders = [root]

    # Append a folder for each section level.
    for i, section_id in enumerate(tid[:depth]):

        # Include the section number and title if the section has a title.
        try:
            section = state.section_titles[tid[: i + 1]]
            section_folder = f"{section_id} {section}"

        # Use only the section number if the section has no title.
        except KeyError:
            section_folder = str(section_id)

        folders.append(section_folder)

    return os.path.join(*folders)
