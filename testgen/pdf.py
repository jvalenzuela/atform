# This module implements generating PDF output.


from . import id
import os


def split_paragraphs(s):
    """Separates a string into a list of paragraphs.

    This function is used to convert a string possibly containing multiple
    paragraphs delimited by empty lines into separate strings, one per
    paragraph, which can then be used by ReportLab Paragraph instances.
    """
    # Assembly buffer to hold lines for each paragraph.
    plines = [
        [] # Inner lists contain lines for a single paragraph.
        # [] Additional inner lists for each additional paragraph.
    ]

    for line in s.splitlines():
        stripped = line.strip()

        # Non-blank lines are appended to the current paragraph's line list.
        if stripped:
            plines[-1].append(stripped)

        # A blank line indicates two or more consecutive newlines, possibly
        # with intervening whitespace, so begin a new line list for a new
        # paragraph.
        else:
            plines.append([])

    # Assemble each non-empty inner list into a paragraph.
    return [' '.join(lines) for lines in plines if lines]


def build_path(tid, root):
    """Constructs a path where a test's output PDF will be written.

    The path will consist of the root, followed by a folder per
    section number, e.g., <root>/<x>/<y> for an ID x.y.z. The final
    number in an ID is not translated to a folder.
    """
    folders = [root]

    # Append a folder for each section level.
    for i in range(len(tid) - 1):

        # Include the section number and title if the section has a title.
        try:
            section = id.section_titles[tid[:i + 1]]
            section_folder = "{0} {1}".format(tid[i], section)

        # Use only the section number if the section has no title.
        except KeyError:
            section_folder = str(tid[i])

        folders.append(section_folder)

    return os.path.join(*folders)
