"""Functions for separating a string into distinct ReportLab paragraphs."""

from reportlab.platypus import Paragraph

from .textstyle import stylesheet


def split_paragraphs(s):
    """Separates a string into a list of paragraphs.

    This function is used to convert a string possibly containing multiple
    paragraphs delimited by empty lines into separate strings, one per
    paragraph, which can then be used by ReportLab Paragraph instances.
    """
    # Assembly buffer to hold lines for each paragraph.
    plines = [
        []  # Inner lists contain lines for a single paragraph.
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
    return [" ".join(lines) for lines in plines if lines]


def make_paragraphs(text):
    """
    Creates a set of flowables from a string containing one or
    more paragraphs.
    """
    flowables = []

    # Set style for the leading paragraph.
    style = "FirstParagraph"

    for ptext in split_paragraphs(text):
        flowables.append(Paragraph(ptext, style=stylesheet[style]))

        # Set style for all paragraphs after the first.
        style = "NextParagraph"

    return flowables
