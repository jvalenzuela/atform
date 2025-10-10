"""Functions for separating a string into distinct ReportLab paragraphs."""

from reportlab.platypus import Flowable, Paragraph

from .textstyle import stylesheet


def split_paragraphs(s: str) -> list[str]:
    """Separates a string into a list of paragraphs.

    This function is used to convert a string possibly containing multiple
    paragraphs delimited by empty lines into separate strings, one per
    paragraph, which can then be used by ReportLab Paragraph instances.
    """
    # Assembly buffer to hold lines for each paragraph.
    plines: list[list[str]] = [
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


def make_paragraphs(text: str) -> list[Flowable]:
    """
    Creates a set of flowables from a string containing one or
    more paragraphs.
    """
    style = stylesheet["Normal"]
    return [Paragraph(p, style=style) for p in split_paragraphs(text)]
