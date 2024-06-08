# This module implements generating PDF output.


from . import id
import itertools
import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.platypus.flowables import Flowable


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


class TestDocument(object):
    """This class creates a PDF for a single Test instance."""

    # Vertical space allotted for the Notes section.
    NOTES_AREA_SIZE = 4 * inch

    def __init__(self, test, root):
        self.test = test

        # The full name is the combination of the test's numeric
        # identifer and title.
        self.full_name = ' '.join((id.to_string(test.id), test.title))

        self._setup_styles()
        doc = self._get_doc(root)
        doc.build(self._build_body())

    def _setup_styles(self):
        """Configures the style sheet."""
        self.style = getSampleStyleSheet()

        # Avoid page breaks between headings and the first flowable in the
        # section.
        for name in self.style.byName:
            if name.startswith('Heading'):
                self.style[name].keepWithNext = 1

    def _get_doc(self, root):
        """Creates the document template."""
        filename = self.full_name + '.pdf'
        path = build_path(self.test.id, root)
        os.makedirs(path, exist_ok=True)
        return SimpleDocTemplate(os.path.join(path, filename))

    def _build_body(self):
        """
        Assembles the list of flowables representing all content other
        than the header and footer.
        """
        # The body is assembled from this list of methods, each
        # returning a list of flowables containing their respective
        # content.
        return list(itertools.chain(
            self._title(),
            self._objective(),
            self._preconditions(),
            self._notes(),
        ))

    def _title(self):
        """Generates the title flowables."""
        return [Paragraph(self.full_name, self.style['Title'])]

    def _objective(self):
        """Generates Objective section flowables."""
        flowables = []
        if self.test.objective:
            flowables.append(self._heading(1, 'Objective'))
            [flowables.append(Paragraph(p))
             for p in split_paragraphs(self.test.objective)]
        return flowables

    def _preconditions(self):
        """Generates Preconditions section flowables."""
        flowables = []
        if self.test.preconditions:
            flowables.append(self._heading(1, 'Preconditions'))

            bullet_list_items = []

            # Create a list of paragraphs for each precondition item.
            for pc in self.test.preconditions:
                bullet_list_items.append([Paragraph(p)
                                          for p in split_paragraphs(pc)])

            flowables.append(ListFlowable(bullet_list_items,
                                          bulletType='bullet'))
        return flowables

    def _notes(self):
        """Generates the Notes section flowables."""
        return [
            self._heading(1, 'Notes'),
            Spacer(0, self.NOTES_AREA_SIZE),
        ]

    def _heading(self, level, text):
        """Creates a flowable containing a section heading."""
        return Paragraph(text, style=self.style['Heading' + str(level)])


class Checkbox(Flowable):
    """A custom flowable that generates an empty checkbox.

    This is used instead of a existing text symbol, such as U+2610,
    because those glyphs are not present in the default PDF fonts.
    """

    # Height and width of the box.
    SIZE = 0.15 * inch

    def wrap(self, *args):
        return (self.SIZE, self.SIZE)

    def draw(self):
        self.canv.rect(0, 0, self.SIZE, self.SIZE)
