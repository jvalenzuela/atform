"""Objects to store test procedure content."""

import os

from . import error
from . import pdf
from . import state
from . import vcs


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


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def generate(path="pdf", folder_depth=0):
    """Builds PDF output files for all defined tests.

    Should be called once near the end of the script after tests have been
    created with :py:class:`atform.Test`.

    .. warning::

        The generated tests will *overwrite* files in the output directory.
        Any content in the output directory that needs to be preserved
        must be copied elsewhere before generating output documents.

    Args:
        path (str, optional): Output directory where PDFs will be saved.
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

    for t in state.tests:
        test_path = build_path(t.id, path, folder_depth)
        pdf.TestDocument(t, test_path, version)
