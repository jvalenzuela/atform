# This module implements generating PDF output.


from . import (
    field,
    id,
    ref,
    sig,
)
import io
import itertools
import os
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    ListFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable


# Constant denoting the point unit of measure(1/72 inch). The unity value
# is because points are the default unit for ReportLab, so a conversion
# constant is not strictly necessary, however, this provides an explicit
# notation consistent with other units imported from reportlab.lib.units.
point = 1


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

    HEADER_TEXT_STYLE = 'Heading2'
    FOOTER_TEXT_STYLE = 'Normal'

    # Vertical distance between the header rule and the top of the page.
    HEADER_HEIGHT = 0.75 * inch

    # Vertical distance between the footer rule and the bottom of the page.
    FOOTER_HEIGHT = 0.5 * inch

    # Left and right margin for header and footer.
    HEADER_FOOTER_SIDE_MARGIN = 0.75 * inch

    # Thickness of the horizontal rules separating the header and footer.
    HEADER_RULE_WEIGHT = 0.5 * point

    # Vertical space allotted for the Notes section.
    NOTES_AREA_SIZE = 4 * inch

    # Thickness of the signature block field underlining.
    SIG_RULE_WEIGHT = 0.2 * point

    # Distance between signature block columns. This spacing is implemented
    # with blank columns of this width instead of left/right padding because
    # padding does not break rules drawn by LINEBELOW, which is how
    # the underlines are created.
    SIG_COL_SEP = 0.2 * inch

    # Width of the signature block Date column.
    SIG_DATE_WIDTH = 0.5 * inch

    # Height of the signature block rows to allow handwritten entries.
    SIG_ROW_HEIGHT = 0.5 * inch

    # Name of the text style used for section headers.
    HEADING_STYLE = 'Heading1'

    # Vertical space above section headers.
    HEADING_SPACE_ABOVE = 24 * point

    def __init__(self, test, root):
        self.test = test

        # The full name is the combination of the test's numeric
        # identifer and title.
        self.full_name = ' '.join((id.to_string(test.id), test.title))

        self._setup_styles()

        # The document is built twice; the first time to a dummy memory
        # buffer in order to determine the total page count, and the
        # second time to the output PDF file.
        for dst in [None, root]:
            doc = self._get_doc(dst)
            doc.build(
                self._build_body(),
                onFirstPage=self._draw_header_footer,
                onLaterPages=self._draw_header_footer,
            )

            # Capture the final page count for the next build.
            self.total_pages = doc.page

    def _setup_styles(self):
        """Configures the style sheet."""
        self.style = getSampleStyleSheet()

        # Avoid page breaks between headings and the first flowable in the
        # section.
        self.style[self.HEADING_STYLE].keepWithNext = 1

        self.style[self.HEADING_STYLE].spaceBefore = self.HEADING_SPACE_ABOVE

    def _get_doc(self, root):
        """Creates the document template."""
        # Output a PDF if root is a string containing a directory.
        if isinstance(root, str):
            pdfname = self.full_name + '.pdf'
            path = build_path(self.test.id, root)
            os.makedirs(path, exist_ok=True)
            filename = os.path.join(path, pdfname)

        # Target a dummy buffer if no directory was provided.
        else:
            filename = io.BytesIO()

        return SimpleDocTemplate(filename)

    def _draw_header_footer(self, canvas, doc):
        """Draws the header and footer."""
        self._header(canvas, doc)
        self._footer(canvas, doc)

    def _header(self, canvas, doc):
        """Draws the page header."""
        self._set_canvas_text_style(canvas, self.HEADER_TEXT_STYLE)
        baseline = doc.pagesize[1] - self.HEADER_HEIGHT
        self._draw_head_foot_rule(canvas, doc, baseline)

        # Offset the text above the rule relative to the font size.
        baseline += self.style[self.HEADER_TEXT_STYLE].fontSize * 0.25

        canvas.drawString(self.HEADER_FOOTER_SIDE_MARGIN,
                          baseline,
                          self.full_name)

    def _footer(self, canvas, doc):
        """Draws the page footer."""
        self._set_canvas_text_style(canvas, self.FOOTER_TEXT_STYLE)
        baseline = self.FOOTER_HEIGHT
        self._draw_head_foot_rule(canvas, doc, baseline)

        # Offset text below the rule relative to the font size.
        baseline -= self.style[self.FOOTER_TEXT_STYLE].fontSize * 1.2

        # See if a total page count is available.
        try:
            total_pages = self.total_pages
        except AttributeError:
            total_pages = '?'

        pages = "Page {0} of {1}".format(doc.page, total_pages)
        canvas.drawCentredString(doc.pagesize[0] / 2, baseline, pages)

    def _set_canvas_text_style(self, canvas, style):
        """Sets the current canvas font to a given style."""
        style = self.style[style]
        canvas.setFont(style.fontName, style.fontSize)

    def _draw_head_foot_rule(self, canvas, doc, y):
        """Draws the horizontal rule for the header and footer."""
        canvas.setLineWidth(self.HEADER_RULE_WEIGHT)
        canvas.line(self.HEADER_FOOTER_SIDE_MARGIN,
                    y,
                    doc.pagesize[0] - self.HEADER_FOOTER_SIDE_MARGIN,
                    y)

    def _build_body(self):
        """
        Assembles the list of flowables representing all content other
        than the header and footer.
        """
        # The body is assembled from this list of methods, each
        # returning a list of flowables containing their respective
        # content.
        return list(itertools.chain(
            self._objective(),
            self._references(),
            self._environment(),
            self._preconditions(),
            self._procedure(),
            self._notes(),
            self._approval(),
        ))

    def _objective(self):
        """Generates Objective section flowables."""
        flowables = []
        if self.test.objective:
            flowables.append(self._heading('Objective'))
            [flowables.append(Paragraph(p))
             for p in split_paragraphs(self.test.objective)]
        return flowables

    def _references(self):
        """Generates References flowables."""
        flowables = []
        if self.test.references:
            flowables.append(self._heading('References'))

            style = self.style['Normal']

            # Generate a row for each reference category.
            rows = [
                [Preformatted(ref.titles[label], style),
                 Paragraph(', '.join(self.test.references[label]), style)]
                for label in self.test.references
            ]

            column_widths = [
                # First column is sized to fit the longest category title.
                max([stringWidth(
                    ref.titles[label],
                    style.fontName,
                    style.fontSize)
                     for label in self.test.references]),

                # Second column gets all remaining space.
                None,
            ]

            # Include LEFTPADDING and RIGHTPADDING.
            column_widths[0] = column_widths[0] + (12 * point)

            table_style = TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5 * point, colors.black),
            ])

            flowables.append(Table(
                rows,
                colWidths=column_widths,
                style=table_style,
            ))

        return flowables

    def _preconditions(self):
        """Generates Preconditions section flowables."""
        flowables = []
        if self.test.preconditions:
            flowables.append(self._heading('Preconditions'))

            bullet_list_items = []

            # Create a list of paragraphs for each precondition item.
            for pc in self.test.preconditions:
                bullet_list_items.append([Paragraph(p)
                                          for p in split_paragraphs(pc)])

            flowables.append(ListFlowable(bullet_list_items,
                                          bulletType='bullet'))
        return flowables

    def _procedure(self):
        """Creates the Procedure section flowables."""
        flowables = []
        if self.test.procedure:
            flowables.append(self._heading('Procedure'))
            rows = []

            # Add header row.
            rows.append(['Step #', 'Description', 'Pass'])

            # Add rows for each procedure step.
            for i in range(len(self.test.procedure)):
                text = [Paragraph(s)
                        for s in split_paragraphs(self.test.procedure[i])]
                rows.append([i + 1, text, Checkbox()])

            column_widths = self._procedure_column_widths(rows[0])
            style = self._procedure_style()
            flowables.append(Table(
                rows,
                colWidths=column_widths,
                style=style,
                repeatRows=1,
            ))

        return flowables

    def _procedure_column_widths(self, header):
        """Computes column widths for the procedure table.

        The widths are derived from the width needed to contain header
        text of the step number and checkbox columns; The description
        column consumes all remaining width.
        """
        style = self.style['Normal']
        widths = [stringWidth(s, style.fontName, style.fontSize)
                  for s in header]

        # Leave the description coulumn undefined as it will be
        # dynamically sized by ReportLab.
        widths[1] = None

        return widths

    def _procedure_style(self):
        """Defines the style applied to the procedure table."""
        return TableStyle([
            # Header row
            ('LINEBELOW', (0, 0), (-1, 0), 2 * point, colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

            # Step rows
            ('LINEBELOW', (0, 1), (-1, -1), .2 * point, colors.black),

            # Step number column
            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),

            # Checkbox column
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (2, 1), (2, -1), 'MIDDLE'),
        ])

    def _notes(self):
        """Generates the Notes section flowables."""
        return [
            self._heading('Notes'),
            Spacer(0, self.NOTES_AREA_SIZE),
        ]

    def _environment(self):
        """Generates the Environment section flowables.

        This section is structured as a table with a row per field.
        """
        flowables = []
        if field.lengths:
            flowables.append(self._heading('Environment'))

            style = self.style['Normal']
            rows = [[Preformatted(t, style),
                     TextEntryField(field.lengths[t], style)]
                    for t in field.lengths]

            # Field title widths for column 0.
            widths = [[stringWidth(t, style.fontName, style.fontSize)
                       for t in field.lengths]]

            # Form field widths for column 1.
            widths.append([row[1].wrap()[0] for row in rows])

            # Column widths are set to the widest entry in each column.
            col_widths = [max(x) for x in widths]

            table_style = TableStyle([
                # Remove unnecessary left padding from title column.
                ('LEFTPADDING', (0 ,0), (0, -1), 0 * point),
            ])

            flowables.append(Table(
                rows,
                colWidths=col_widths,
                style=table_style,
                hAlign='LEFT',
            ))
        return flowables

    def _approval(self):
        """Generates the Approval section flowables."""
        flowables = []
        if sig.titles:
            style = self.style['Normal']
            flowables.append(self._heading('Approval'))
            table_data = []

            # Start with header row.
            table_data.append(
                [Preformatted(s, style=style) for s in [
                    '', '', 'Name', '', 'Signature', '', 'Date']])

            # Append rows for each title.
            [table_data.append([Preformatted(s, style=style)])
             for s in sig.titles]

            style = TableStyle([
                # Add underlines for entry fields.
                self._sig_rule(2),
                self._sig_rule(4),
                self._sig_rule(6),

                # Remove all padding around cell content.
                ('LEFTPADDING', (0 ,0), (-1, -1), 0 * point),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0 * point),
                ('TOPPADDING', (0, 0), (-1, -1), 0 * point),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0 * point),
            ])

            row_heights = [None] # Default height for header row.
            row_heights.extend([self.SIG_ROW_HEIGHT] * len(sig.titles))

            flowables.append(Table(
                table_data,
                style=style,
                colWidths = self._sig_col_widths(),
                rowHeights = row_heights,
            ))
        return flowables

    def _sig_col_widths(self):
        """Computes the column widths of the signature block table."""
        style = self.style['Normal']

        return [
            # Width of the first column is set to accommodate the
            # longest title.
            max([stringWidth(s, style.fontName, style.fontSize)
                 for s in sig.titles]),

            self.SIG_COL_SEP,

            # Remaining area is split between the Name and Signature fields.
            None,
            self.SIG_COL_SEP,
            None,

            self.SIG_COL_SEP,
            self.SIG_DATE_WIDTH
        ]

    def _sig_rule(self, col):
        """Creates an underline for a signature block column."""
        return ('LINEBELOW', (col, 1), (col, -1), self.SIG_RULE_WEIGHT,
                colors.black)

    def _heading(self, text):
        """Creates a flowable containing a section heading."""
        return Paragraph(text, style=self.style[self.HEADING_STYLE])


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


class TextEntryField(Flowable):
    """Creates an Acroform for entering a single line of text."""

    # Border thickness.
    BORDER_WEIGHT = 0.5 * point

    # Coefficient applied to the font size to calculate box height.
    HEIGHT_FACTOR = 2

    def __init__(self, max_chars, style):
        self.style = style

        # Width is calculated to hold the given maximum string length.
        self.width = stringWidth(
            'X' * max_chars,
            style.fontName,
            style.fontSize,
        )

        self.height = style.fontSize * self.HEIGHT_FACTOR

    def wrap(self, *args):
        return (self.width, self.height)

    def draw(self):
        self.canv.acroForm.textfield(
            width = self.width,
            height = self.height,
            fontName = self.style.fontName,
            fontSize = self.style.fontSize,
            borderWidth = self.BORDER_WEIGHT,
            relative=True,
        )
