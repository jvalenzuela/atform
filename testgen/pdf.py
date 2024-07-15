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
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    ListFlowable,
    ListItem,
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


def make_paragraphs(text, style_sheet):
    """
    Creates a set of flowables from a string containing one or
    more paragraphs.
    """
    flowables = []

    # Set style for the leading paragraph.
    style = style_sheet['FirstParagraph']

    for ptext in split_paragraphs(text):
        flowables.append(Paragraph(ptext, style=style))

        # Set style for all paragraphs after the first.
        style = style_sheet['NextParagraph']

    return flowables


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


def create_text_style():
    """Generates a style sheet for all text styles.

    All fonts are chosen from the 14 standard PDF fonts to ensure
    maximum compatibility with PDF readers, without embedding font
    encodings. Reference PDF 1.7, Adobe Systems, First Edition 2008-7-1,
    section 9.6.2.2.

    Use of a serifed typeface, Times Roman, as the default is per
    typographical convention, and leaves sans-serif available
    for use with setting verbatim text.
    """
    style = getSampleStyleSheet()

    style['Normal'].fontName = 'Times-Roman'
    style['Normal'].fontSize = 12

    style.add(ParagraphStyle(
        name='NormalCentered',
        parent=style['Normal'],
        alignment=TA_CENTER,
    ))

    style.add(ParagraphStyle(
        name='SectionHeading',
        parent=style['Heading1'],
        fontName='Times-Bold',

        # Avoid page breaks between the heading and the first flowable in
        # the section.
        keepWithNext=1,

        spaceBefore=24 * point,
    ))

    # Leading paragraph in a body of text.
    style.add(ParagraphStyle(
        name='FirstParagraph',
        parent=style['Normal'],
    ))

    # Any additional paragraphs in a body of text.
    style.add(ParagraphStyle(
        name='NextParagraph',
        parent=style['FirstParagraph'],
        spaceBefore=4 * point,
        firstLineIndent=0.25 * inch,
    ))

    style.add(ParagraphStyle(
        name='Header',
        parent=style['Heading2'],
        fontName='Times-Bold',
    ))

    style.add(ParagraphStyle(
        name='Footer',
        parent=style['Normal'],
    ))

    style.add(ParagraphStyle(
        name='ProcedureTableHeading',
        parent=style['Normal'],
        fontName='Times-Bold',
        alignment=TA_CENTER,
    ))

    return style


class TestDocument(object):
    """This class creates a PDF for a single Test instance."""

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

    # Vertical space between bullet list items.
    BULLET_LIST_SKIP = 12 * point

    style = create_text_style()

    def __init__(self, test, root):
        self.test = test

        # The full name is the combination of the test's numeric
        # identifer and title.
        self.full_name = ' '.join((id.to_string(test.id), test.title))

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

        return SimpleDocTemplate(filename, pagesize=letter)

    def _draw_header_footer(self, canvas, doc):
        """Draws the header and footer."""
        self._header(canvas, doc)
        self._footer(canvas, doc)

    def _header(self, canvas, doc):
        """Draws the page header."""
        self._set_canvas_text_style(canvas, 'Header')
        baseline = doc.pagesize[1] - self.HEADER_HEIGHT
        self._draw_head_foot_rule(canvas, doc, baseline)

        # Offset the text above the rule relative to the font size.
        baseline += self.style['Header'].fontSize * 0.25

        canvas.drawString(self.HEADER_FOOTER_SIDE_MARGIN,
                          baseline,
                          self.full_name)

        self._header_project_info(canvas, doc, baseline)

    def _header_project_info(self, canvas, doc, baseline):
        """Draws project information in the header.

        All project information fields are located on the right side
        of the header, however, the vertical order in which they are
        presented is dynamically adjusted to avoid empty lines between
        the text and header rule. E.g., if the project information
        dictionary has only one key, it will always rest directly on
        the header rule.
        """

        # Assemble the content of each line, ordered from bottom up.
        lines = [self.test.project_info.get(key)
                 for key in [
                         'system',
                         'project',
                 ]]

        right_margin = doc.pagesize[0] - self.HEADER_FOOTER_SIDE_MARGIN

        # Draw available lines, starting from the bottom.
        for line in lines:
            if line:
                canvas.drawRightString(right_margin, baseline, line)
                baseline += self.style['Header'].fontSize * 1.2

    def _footer(self, canvas, doc):
        """Draws the page footer."""
        self._set_canvas_text_style(canvas, 'Footer')
        baseline = self.FOOTER_HEIGHT
        self._draw_head_foot_rule(canvas, doc, baseline)

        # Offset text below the rule relative to the font size.
        baseline -= self.style['Footer'].fontSize * 1.2

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
            self._equipment(),
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
            flowables.extend(make_paragraphs(self.test.objective, self.style))
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

    def _equipment(self):
        """Generates the Required Equipment section flowables."""
        flowables = []
        if self.test.equipment:
            flowables.append(self._heading('Required Equipment'))
            flowables.append(self._bullet_list(self.test.equipment))
        return flowables

    def _preconditions(self):
        """Generates Preconditions section flowables."""
        flowables = []
        if self.test.preconditions:
            flowables.append(self._heading('Preconditions'))
            flowables.append(self._bullet_list(self.test.preconditions))
        return flowables

    def _procedure(self):
        """Creates the Procedure section flowables."""
        flowables = []
        if self.test.procedure:
            flowables.append(self._heading('Procedure'))

            proc = ProcedureList(self.test.procedure, self.style)
            flowables.append(proc.flowable)

        return flowables

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
            flowables.append(Approval(style).flowable)
        return flowables

    def _heading(self, text):
        """Creates a flowable containing a section heading."""
        return Preformatted(text, style=self.style['SectionHeading'])

    def _bullet_list(self, items):
        """Create a bullet list flowable."""
        return ListFlowable(

            # Each item may contain multiple paragraphs, which are
            # expanded to a list of strings.
            [ListItem(
                make_paragraphs(i, self.style),
                spaceBefore=self.BULLET_LIST_SKIP,
                )
             for i in items],

            bulletType='bullet',
        )


class ProcedureList(object):
    """Constructs the flowable containing the entire procedure list.

    The procedure list is built as a table, with one row per step.
    """

    # Thickness of the horizontal rule under the header row.
    HEADER_RULE_WEIGHT = 2 * point

    # Thickness of the horizontal rules between each step.
    STEP_RULE_WEIGHT = 0.2 * point

    # Vertical space between the text and data entry fields in a
    # single procedure step.
    FIELD_TABLE_SEP = 12 * point

    # Horizontal space between columns in table containing the
    # data entry fields for a step.
    FIELD_TABLE_HORIZ_PAD = 6 * point

    # Header row text.
    HEADER_FIELDS = ['Step #', 'Description', 'Pass']

    def __init__(self, steps, style_sheet):
        self.steps = steps
        self.style_sheet = style_sheet
        self.rows = []
        self._add_header()
        self._add_steps()
        self._add_last_row()

    def _add_header(self):
        """Generates the header row."""
        style = self.style_sheet['ProcedureTableHeading']
        row = [Paragraph(s, style) for s in self.HEADER_FIELDS]
        self.rows.append(row)

    def _add_steps(self):
        """Adds rows for all steps."""
        style = self.style_sheet['NormalCentered']
        for i in range(len(self.steps)):
            desc = self._step_body(self.steps[i])
            step_num = Paragraph(str(i + 1), style)
            self.rows.append([step_num, desc, Checkbox()])

    def _step_body(self, step):
        """
        Creates flowables containing all user-defined content for a single
        step, i.e., everything that goes in the Description column.
        """
        # Begin with the step instruction text.
        flowables = make_paragraphs(step['text'], self.style_sheet)

        try:
            fields = step['fields']

        except KeyError:
            pass # Fields are optional.

        else:
            if fields:
                flowables.append(Spacer(0, self.FIELD_TABLE_SEP))
                flowables.append(self._make_fields(fields))

        return flowables

    def _make_fields(self, fields):
        """Makes a flowable with all data entry fields for a single step.

        Fields are arranged into a table, with one row per field.
        """
        style = self.style_sheet['Normal']
        rows = []
        for field in fields:
            row = [
                Preformatted(field.title, style),
                TextEntryField(field.length, style),
            ]

            # Add the optional suffix if it exists.
            if field.suffix:
                row.append(Preformatted(field.suffix, style))

            rows.append(row)

        return Table(
            rows,
            colWidths=self._field_table_widths(rows),
            style=self._field_table_style,
        )

    def _field_table_widths(self, rows):
        """
        Computes the column widths for a table containing data entry
        fields in a single step.
        """
        widths = []

        widths.append([row[0].minWidth() for row in rows])
        widths.append([row[1].minWidth() for row in rows])

        max_widths = [max(l) + self.FIELD_TABLE_HORIZ_PAD for l in widths]

        # The last column for the suffix takes up all remaining space.
        max_widths.append(None)

        return max_widths

    def _add_last_row(self):
        """Creates the final row indicating the end of the procedure."""
        style = self.style_sheet['ProcedureTableHeading']
        text = Paragraph('End Procedure', style)
        self.rows.append([None, text, None])

    @property
    def _field_table_style(self):
        """
        Creates the style for table containing data entry fields in a
        single step.
        """
        return TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0 * point),
        ])

    @property
    def flowable(self):
        """Generates the flowable representing the entire procedure list."""
        return Table(
            self.rows,
            colWidths=self._column_widths,
            style=self._table_style,
            repeatRows=1,
        )

    @property
    def _column_widths(self):
        """Computes column widths for the overall table.

        The widths are derived from the width needed to contain header
        text of the step number and checkbox columns; the description
        column consumes all remaining width.
        """
        style = self.style_sheet['ProcedureTableHeading']
        widths = [stringWidth(s, style.fontName, style.fontSize)
                  for s in self.HEADER_FIELDS]

        # Leave the description column undefined as it will be
        # dynamically sized by ReportLab.
        widths[1] = None

        return widths

    @property
    def _table_style(self):
        """Style applied to the entire procedure list table."""
        return TableStyle([
            # Header row
            ('LINEBELOW', (0, 0), (-1, 0), self.HEADER_RULE_WEIGHT, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

            # Step rows
            ('LINEBELOW', (0, 1), (-1, -3), self.STEP_RULE_WEIGHT, colors.black),

            # Step number column
            ('VALIGN', (0, 1), (0, -2), 'MIDDLE'),

            # Checkbox column
            ('ALIGN', (2, 1), (2, -2), 'CENTER'),
            ('VALIGN', (2, 1), (2, -2), 'MIDDLE'),

            # Last row
            ('LINEABOVE', (0, -1), (-1, -1), self.HEADER_RULE_WEIGHT,
             colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),

            # Remove padding between all columns.
            ('LEFTPADDING', (0 ,0), (-1, -1), 0 * point),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0 * point),
        ])


class Approval(object):
    """Creates a flowable implementing approval signatures.

    This is implemented as a table with one row per signature.
    """

    # Thickness of the signature underline.
    RULE_WEIGHT = 0.2 * point

    # Distance between table columns. This spacing is implemented
    # with blank columns of this width instead of left/right padding because
    # padding does not break rules drawn by LINEBELOW, which is how
    # the underlines are created.
    COL_SEP = 0.2 * inch

    # Number of characters the name text entry fields should be sized to
    # accommodate.
    NAME_WIDTH = 15

    # Height of the table rows to allow handwritten entries.
    ROW_HEIGHT = 0.5 * inch

    def __init__(self, style):
        self.style = style
        self.rows = []

        # Start with header row.
        self.rows.append(
            [Preformatted(s, style=style) for s in [
                '', '', 'Name', '', 'Signature', '', 'Date']])

        # Append rows for each title.
        [self.rows.append(self._make_row(title)) for title in sig.titles]

    def _make_row(self, title):
        """Generates a row for a given signature entry."""
        return [
            Preformatted(title, style=self.style),
            None,
            TextEntryField(self.NAME_WIDTH, self.style),
            None,
            None,
            None,
            TextEntryField(len('YYYY/MM/DD'), self.style),
        ]

    @property
    def _table_style(self):
        """Generates the table style."""
        return TableStyle([
            # Signature column underline.
            ('LINEBELOW', (4, 1), (4, -1), self.RULE_WEIGHT, colors.black),

            # Remove all padding around cell content.
            ('LEFTPADDING', (0 ,0), (-1, -1), 0 * point),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0 * point),
            ('TOPPADDING', (0, 0), (-1, -1), 0 * point),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0 * point),
        ])

    @property
    def _col_widths(self):
        """Computes the column widths of the signature block table."""
        return [
            # Width of the first column is set to accommodate the
            # longest title.
            max([stringWidth(s, self.style.fontName, self.style.fontSize)
                 for s in sig.titles]),

            self.COL_SEP,

            # Name column is sized based on the text entry field.
            self._get_text_entry_field_width(2),

            self.COL_SEP,

            None, # Remaining area given to the Signature field.

            self.COL_SEP,

            # Date column is sized based on the text entry field.
            self._get_text_entry_field_width(6),
        ]

    def _get_text_entry_field_width(self, column):
        """Acquires the width of a text entry field from a given column."""
        # Use the first row after the header as the text entry
        # fields are the same in every column.
        row = self.rows[1]

        return row[column].wrap()[0]

    @property
    def _row_heights(self):
        """Computes the height of all table rows."""
        heights = [None] # Default height for header row.
        heights.extend([self.ROW_HEIGHT] * len(sig.titles))
        return heights

    @property
    def flowable(self):
        """Generates the flowable containing the entire approval block."""
        return Table(
            self.rows,
            style=self._table_style,
            colWidths=self._col_widths,
            rowHeights=self._row_heights,
        )


class Checkbox(Flowable):
    """A custom flowable that generates a form checkbox."""

    # Height and width of the box.
    SIZE = 0.25 * inch

    def wrap(self, *args):
        return (self.SIZE, self.SIZE)

    def draw(self):
        self.canv.acroForm.checkbox(
            size=self.SIZE,
            relative=True,
        )


class TextEntryField(Flowable):
    """Creates an Acroform for entering a single line of text."""

    # Border thickness.
    BORDER_WEIGHT = 0.5 * point

    # Coefficient applied to the font size to calculate box height.
    HEIGHT_FACTOR = 1.2

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
