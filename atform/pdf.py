# This module implements generating PDF output.


from . import (
    field,
    id,
    ref,
    sig,
)
from .textstyle import (
    point,
    stylesheet,
)
import functools
import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
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


LEFT_MARGIN = 0.75 * inch
RIGHT_MARGIN = LEFT_MARGIN
TOP_MARGIN = 0.75 * inch
BOTTOM_MARGIN = 0.5 * inch


# Default left and right padding for table cells, i.e., default value for
# LEFTPADDING and RIGHTPADDING table style commands.
DEFAULT_TABLE_HORIZ_PAD = 6 * point


# Thickness of lines separating top-level sections and divisions within
# each section.
SECTION_RULE_WEIGHT = 1 * point
SUBSECTION_RULE_WEIGHT = 0.5 * point


# Color for all rules(lines).
RULE_COLOR = colors.black


# Vertical space between each top-level section.
SECTION_SEP = 5 * point


# Vertical space allotted for the Notes section.
NOTES_AREA_SIZE = 2 * inch


# Text color for the draft watermark.
DRAFTMARK_COLOR = colors.Color(0, 0, 0, 0.3)


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


def make_paragraphs(text):
    """
    Creates a set of flowables from a string containing one or
    more paragraphs.
    """
    flowables = []

    # Set style for the leading paragraph.
    style = 'FirstParagraph'

    for ptext in split_paragraphs(text):
        flowables.append(Paragraph(ptext, style=stylesheet[style]))

        # Set style for all paragraphs after the first.
        style = 'NextParagraph'

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


def max_width(items, style_name):
    """Finds the width required to hold the longest among a set of strings.

    Used to size a table column such that it can hold the content
    of all rows in that column.
    """
    style = stylesheet[style_name]
    widths = [stringWidth(i, style.fontName, style.fontSize)
              for i in items]

    # The final width includes left and right table padding.
    return max(widths) + (DEFAULT_TABLE_HORIZ_PAD * 2)


class TableFormat(object):
    """
    This class contains methods for generating table style commands (tuples)
    for common formatting elements.
    """

    def table_style_cmd(method):
        """Decorator for methods that create a table style command."""
        @functools.wraps(method)
        def wrapper(*seq):
            # Convert the given arguments into a mutable list.
            items = list(seq)

            # Wrapped method will alter the argument list.
            method(items)

            # Return the completed list of arguments as a tuple.
            return tuple(items)

        return staticmethod(wrapper)

    @table_style_cmd
    def section_rule(seq):
        """Line separating the top-level section tables."""
        seq.append(SECTION_RULE_WEIGHT)
        seq.append(RULE_COLOR)

    @table_style_cmd
    def subsection_rule(seq):
        """Line separating content within a section."""
        seq.append(SUBSECTION_RULE_WEIGHT)
        seq.append(RULE_COLOR)

    @table_style_cmd
    def section_background(seq):
        """Background for top-level section titles."""
        seq.insert(0, 'BACKGROUND')
        seq.append(colors.lightsteelblue)

    @table_style_cmd
    def subsection_background(seq):
        """Background for divisions within a section."""
        seq.insert(0, 'BACKGROUND')
        seq.append(colors.lightgrey)


class TestDocument(object):
    """This class creates a PDF for a single Test instance."""

    def __init__(self, test, root, draft, version):
        self.test = test
        self.draft = draft
        self.version = version

        # The full name is the combination of the test's numeric
        # identifier and title.
        self.full_name = ' '.join((id.to_string(test.id), test.title))

        # The document is built twice; the first time to a dummy memory
        # buffer in order to determine the total page count, and the
        # second time to the output PDF file.
        for dst in [None, root]:
            self.doc = self._get_doc(dst)
            self.doc.build(
                self._build_body(),
                onFirstPage=self._on_every_page,
                onLaterPages=self._on_every_page,
            )

            # Capture the final page count for the next build.
            self.total_pages = self.doc.page

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

        return SimpleDocTemplate(
            filename,
            pagesize=letter,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=BOTTOM_MARGIN,
        )

    def _on_every_page(self, canvas, doc):
        """Document template callback applied to all pages."""
        if self.draft:
            self._draftmark(canvas, doc)

        self._header(canvas, doc)
        self._footer(canvas, doc)

    def _header(self, canvas, doc):
        """Draws the page header."""
        self._set_canvas_text_style(canvas, 'Header')
        baseline = doc.pagesize[1] - TOP_MARGIN

        canvas.drawString(LEFT_MARGIN,
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

        right_margin = doc.pagesize[0] - RIGHT_MARGIN

        # Draw available lines, starting from the bottom.
        for line in lines:
            if line:
                canvas.drawRightString(right_margin, baseline, line)
                baseline += stylesheet['Header'].fontSize * 1.2

    def _footer(self, canvas, doc):
        """Draws the page footer."""
        self._set_canvas_text_style(canvas, 'Footer')

        # Offset text below the margin relative to the font size.
        baseline = BOTTOM_MARGIN - (stylesheet['Footer'].fontSize * 1.2)

        # See if a total page count is available.
        try:
            total_pages = self.total_pages
        except AttributeError:
            total_pages = '?'

        pages = "Page {0} of {1}".format(doc.page, total_pages)
        canvas.drawCentredString(doc.pagesize[0] / 2, baseline, pages)

        # Add version information if available.
        if not self.draft and self.version:
            x = doc.pagesize[0] - RIGHT_MARGIN
            version_text = "Document Version: {0}".format(self.version)
            canvas.drawRightString(x, baseline, version_text)

    def _set_canvas_text_style(self, canvas, style):
        """Sets the current canvas font to a given style."""
        style = stylesheet[style]
        canvas.setFont(style.fontName, style.fontSize)

    def _build_body(self):
        """
        Assembles the list of flowables representing all content other
        than the header and footer.
        """
        flowables = [
            self._objective(),
            self._references(),
            self._environment(),
            self._equipment(),
            self._preconditions(),
            self._procedure(),
            self._notes(),
            self._approval(),
        ]

        return [f for f in flowables if f]

    def _objective(self):
        """Generates Objective section."""
        if self.test.objective:
            rows = [[make_paragraphs(self.test.objective)]]
            return self._section('Objective', rows)

    def _references(self):
        """Generates References flowables."""
        if self.test.references:
            # Generate a row for each reference category.
            rows = [
                [Paragraph(ref.titles[label], stylesheet['NormalRight']),
                 Paragraph(
                     ', '.join(self.test.references[label]),
                     stylesheet['Normal']
                 )]
                for label in self.test.references
            ]

            titles = [ref.titles[label]
                      for label in self.test.references]

            column_widths = [
                # First column is sized to fit the longest category title.
                max_width(titles, 'NormalRight'),

                # Second column gets all remaining space.
                None,
            ]

            # Include LEFTPADDING and RIGHTPADDING.
            column_widths[0] = column_widths[0] + (2 * DEFAULT_TABLE_HORIZ_PAD)

            table_style = [
                TableFormat.subsection_rule('LINEBEFORE', (1, 1), (1, -1)),
                TableFormat.subsection_rule('LINEABOVE', (0, 2), (-1, -1)),

                # Category column vertical alignment.
                ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
            ]

            return self._section(
                'References',
                rows,
                style=table_style,
                colWidths=column_widths,
            )

    def _equipment(self):
        """Generates the Required Equipment section."""
        if self.test.equipment:
            return self._bullet_list_section(
                'Required Equipment',
                self.test.equipment
                )

    def _preconditions(self):
        """Generates Preconditions section."""
        if self.test.preconditions:
            return self._bullet_list_section(
                'Preconditions',
                self.test.preconditions)

    def _procedure(self):
        """Creates the Procedure section."""
        if self.test.procedure:
            proc = ProcedureList(self.test.procedure)
            return self._section(
                'Procedure',
                proc.rows,
                style=proc.style,
                nosplit=False,
                colWidths=proc.widths,
                repeatRows=(1,),
            )

    def _notes(self):
        """Generates the Notes section."""
        return self._section('Notes', [[Spacer(0, NOTES_AREA_SIZE)]])

    def _environment(self):
        """Generates the Environment section."""
        if self.test.fields:
            rows = [[Paragraph(f.title, stylesheet['NormalRight']),
                     TextEntryField(f.length, 'Normal')]
                    for f in self.test.fields]

            # Field title widths for column 0.
            widths = [
                max_width(
                    [f.title for f in self.test.fields],
                    'NormalRight',
                ),

                # All remaining width to the text entry column.
                None,
            ]

            table_style = [
                # Horiziontal rule between each item.
                TableFormat.subsection_rule('LINEABOVE', (0, 2), (-1, -1)),
            ]

            return self._section(
                'Environment',
                rows,
                colWidths=widths,
                style=table_style,
            )

    def _approval(self):
        """Generates the Approval section."""
        if sig.titles:
            content = Approval()
            return self._section(
                'Approval',
                content.rows,
                style=content.style,
                colWidths=content.widths,
            )

    def _section(self, title, rows, style=[], nosplit=True, **kwargs):
        """Creates a table enclosing an entire top-level section."""
        # Add the title as the first row.
        rows.insert(0, [
            Preformatted(title, stylesheet['SectionHeading'])
        ])

        style.extend([
            # Border surrounding the entire section.
            TableFormat.section_rule('BOX', (0, 0), (-1, -1)),

            # Title row background.
            TableFormat.section_background((0, 0), (0, 0)),

            # The title spans all columns.
            ('SPAN', (0, 0), (-1, 0)),
        ])

        # Keep the entire section together unless the table is
        # explicitly built to handle splitting.
        if nosplit:
            style.append(('NOSPLIT', (0, 0), (-1, -1)))

        self._set_section_table_width(kwargs)

        return Table(
            rows,
            style=style,
            spaceBefore=SECTION_SEP,
            **kwargs,
        )

    def _set_section_table_width(self, table_args):
        """
        Adjusts section table column widths to fill all available
        horizontal space.
        """
        # Target table width is the size of the paper less left and
        # right margins.
        table_width = (self.doc.pagesize[0] - LEFT_MARGIN - RIGHT_MARGIN)

        try:
            widths = table_args['colWidths']

        # Sections with a single column do not specify widths, so that
        # column occupies the entire width.
        except KeyError:
            table_args['colWidths'] = [table_width]

        # Sections with multiple one columns will have one column that
        # will be streteched to occupy all remaining space.
        else:
            stretch_col = widths.index(None)
            remain = table_width - sum([w for w in widths if w])
            widths[stretch_col] = remain

    def _bullet_list_section(self, title, items):
        """Creates a section consisting of a simple bullet list.

        The section is built as a table with one item per row;
        each row is comprised of a ListFlowable with a single
        item to create the bullet list formatting.
        """
        rows = [[ListFlowable(

            # Each item may contain multiple paragraphs, which are
            # expanded to a list of strings.
            [ListItem(make_paragraphs(i))],
            bulletType='bullet',
            )] for i in items]

        return self._section(title, rows)

    def _draftmark(self, canvas, doc):
        """Creates a draft watermark."""
        canvas.saveState()
        self._set_canvas_text_style(canvas, 'Draftmark')

        # Translate origin to center of page.
        canvas.translate(doc.pagesize[0] / 2, doc.pagesize[1] / 2)

        canvas.rotate(45)
        canvas.setFillColor(DRAFTMARK_COLOR)

        # Offset y coordinate by half the font size because the text
        # is anchored at its baseline, not the midpoint.
        y = stylesheet['Draftmark'].fontSize / -2

        canvas.drawCentredString(0, y, 'DRAFT')
        canvas.restoreState()


class ProcedureList(object):
    """Constructs the flowable containing the entire procedure list.

    The procedure list is built as a table, with one row per step.
    """

    # Vertical space between the text and data entry fields in a
    # single procedure step.
    FIELD_TABLE_SEP = 12 * point

    # Horizontal space between columns in table containing the
    # data entry fields for a step.
    FIELD_TABLE_HORIZ_PAD = 6 * point

    # Header row text.
    HEADER_FIELDS = ['Step #', 'Description', 'Pass']

    # Column indices.
    STEP_COL = 0
    DESC_COL = 1
    PASS_COL = 2

    def __init__(self, steps):
        self.steps = steps
        self.rows = []
        self._add_header()
        self._add_steps()
        self._add_last_row()

    def _add_header(self):
        """Generates the header row."""
        style = stylesheet['ProcedureTableHeading']
        row = [Paragraph(s, style) for s in self.HEADER_FIELDS]
        self.rows.append(row)

    def _add_steps(self):
        """Adds rows for all steps."""
        step_style = stylesheet['ProcedureTableHeading']
        for i in range(len(self.steps)):
            desc = self._step_body(self.steps[i])
            step_num = Paragraph(str(i + 1), step_style)
            self.rows.append([step_num, desc, Checkbox()])

    def _step_body(self, step):
        """
        Creates flowables containing all user-defined content for a single
        step, i.e., everything that goes in the Description column.
        """
        # Begin with the step instruction text.
        flowables = make_paragraphs(step.text)

        if step.fields:
                flowables.append(Spacer(0, self.FIELD_TABLE_SEP))
                flowables.append(self._make_fields(step.fields))

        return flowables

    def _make_fields(self, fields):
        """Makes a flowable with all data entry fields for a single step.

        Fields are arranged into a table, with one row per field.
        """
        style = stylesheet['Normal']
        rows = []
        for field in fields:
            row = [
                Preformatted(field.title, style),
                TextEntryField(field.length, 'Normal'),
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
        self.rows.append([
            Paragraph('End Procedure', stylesheet['ProcedureTableHeading'])
        ])

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
    def widths(self):
        """Computes column widths for the overall table."""
        style = 'ProcedureTableHeading'

        widths = []

        # Width of the step column is set to accommodate the larger of
        # the column header text and the last step number.
        step_col_items = [
            self.HEADER_FIELDS[self.STEP_COL],
            str(len(self.steps)),
        ]
        widths.append(max_width(step_col_items, style))

        # Leave the description column undefined as it will be
        # dynamically sized to consume all remaining width.
        widths.append(None)

        # Pass column width is set to accommodate the larger of the
        # column header and checkboxes.
        pass_col_items = [
            max_width([self.HEADER_FIELDS[self.PASS_COL]], style),
            Checkbox().wrap()[0] + (DEFAULT_TABLE_HORIZ_PAD * 2),
        ]

        # Add a miniscule amount of width to the pass column to avoid
        # wrapping the first header row. It is unknown why this is required
        # and only affects the initial header row while repeated header rows
        # on additional pages do not wrap.
        widths.append(max(pass_col_items) + .1)

        return widths

    @property
    def style(self):
        """Style applied to the entire procedure list table."""
        return [
            # Header row shading.
            TableFormat.subsection_background((0, 1), (-1, 1)),

            # Add a section rule above the header row. This is unnecessary
            # on the initial page, however, it's the only way to get
            # a rule on the top of following pages because the 'splitfirst'
            # index doesn't apply to repeated rows.
            TableFormat.section_rule('LINEABOVE', (0, 1), (-1, 1)),

            # Do not split between the section header row and first step.
            ('NOSPLIT', (0, 0), (-1, 2)),

            # Do not split between the final step and last row.
            ('NOSPLIT', (0, -2), (0, -1)),

            # Horizontal rules between each step.
            TableFormat.subsection_rule('LINEBELOW', (0, 2), (-1, -3)),

            # Step number column
            ('VALIGN', (self.STEP_COL, 2), (self.STEP_COL, -2), 'MIDDLE'),

            # Checkbox column
            ('ALIGN', (self.PASS_COL, 2), (self.PASS_COL, -2), 'CENTER'),
            ('VALIGN', (self.PASS_COL, 2), (self.PASS_COL, -2), 'MIDDLE'),

            # Last row shading.
            TableFormat.subsection_background((0, -1), (-1, -1)),

            # Last row spans all columns.
            ('SPAN', (0, -1), (-1, -1)),

            # Add a section rule at the bottom of every page break.
            TableFormat.section_rule(
                'LINEBELOW',
                (0, 'splitlast'),
                (-1, 'splitlast')
            ),
        ]


class Approval(object):
    """Creates table content for the approval section.

    Each signature is built with two rows; the upper row carries the
    titles above each field and the lower row is the actual data entry
    fields.
    """

    # Number of characters the name text entry fields should be sized to
    # accommodate.
    NAME_WIDTH = 15

    # Vertical distance between field names and the data entry fields.
    FIELD_TITLE_SEP = 1 * point

    # Column indices.
    TITLE_COL = 0
    NAME_COL = 1
    SIG_COL = 2
    DATE_COL = 3

    def __init__(self):
        self.rows = []
        [self._make_sig_rows(title) for title in sig.titles]

    def _make_sig_rows(self, title):
        """Generates a row for a given signature entry."""
        field_style = stylesheet['SignatureFieldTitle']

        # Top row has the signature and field titles.
        self.rows.append([
            Paragraph(title, stylesheet['NormalRight']),
            Paragraph('Name', field_style),
            Paragraph('Signature', field_style),
            Paragraph('Date', field_style),
        ])

        # Lower row contains the text entry fields.
        self.rows.append([
            None, # Title column in empty in this row.
            self._name_entry_field(),
            None, # Signature column is blank.
            self._date_entry_field(),
        ])

    def _name_entry_field(self):
        """Creates a name entry field."""
        return TextEntryField(self.NAME_WIDTH, 'Normal')

    def _date_entry_field(self):
        """Creates a date entry field."""
        return TextEntryField(
            '0000/00/00',
            'Normal',
            'YYYY/MM/DD'
        )

    @property
    def style(self):
        """Generates style commands for the entire table."""
        style = [
            # Vertical rules.
            TableFormat.subsection_rule(
                'LINEBEFORE',
                (self.NAME_COL, 1),
                (-1, -1)
            ),

            # Remove all vertical padding around title column as it
            # spans two rows.
            ('TOPPADDING', (self.TITLE_COL, 1), (self.TITLE_COL, -1), 0),
            ('BOTTOMPADDING', (self.TITLE_COL, 1), (self.TITLE_COL, -1), 0),

            # Vertically center the title column.
            ('VALIGN', (self.TITLE_COL, 1), (self.TITLE_COL, -1), 'MIDDLE'),
        ]

        [style.extend(self._sig_row_style(i)) for i in range(len(sig.titles))]

        return style

    def _sig_row_style(self, i):
        """Generates style commands for the two rows of a signature entry."""
        # Calculate the indices for the two rows assigned to this signature.
        upper = (i * 2) + 1
        lower = upper + 1

        style = [
            # Title column spans both upper and lower rows.
            ('SPAN', (self.TITLE_COL, upper), (self.TITLE_COL, lower)),

            # Remove vertical padding above the upper field name row.
            ('TOPPADDING', (self.NAME_COL, upper), (-1, upper), 0),

            # Set padding between the upper and lower row.
            (
                'BOTTOMPADDING',
                (self.NAME_COL, upper),
                (-1, upper),
                self.FIELD_TITLE_SEP
            ),

            # Remove padding above the entire lower row.
            ('TOPPADDING', (0, lower), (-1, lower), 0),
        ]

        # Set left padding for the name and date entry fields so the text
        # entry field abuts the subsection rule to the left.
        [style.append((
            'LEFTPADDING',
            (col, lower),
            (col, lower),
            SUBSECTION_RULE_WEIGHT / 2
        ))
         for col in [self.NAME_COL, self.DATE_COL]]

        last_row = i + 1 == len(sig.titles)
        if not last_row:
            # Rule below all but the last row are subsection rules.
            hrule_weight = SUBSECTION_RULE_WEIGHT

            # Horizontal rule beween each signature, except below the last
            # row because it's closed by a section rule.
            style.append(TableFormat.subsection_rule(
                'LINEBELOW',
                (0, lower),
                (-1, lower)
            ))
        else:
            # Rule below the last row is a section rule.
            hrule_weight = SECTION_RULE_WEIGHT

        # Set padding below the data entry fields so they rest on the
        # rule below them.
        [style.append((
            'BOTTOMPADDING',
            (col, lower),
            (col, lower),
            hrule_weight / 2))
         for col in [self.NAME_COL, self.DATE_COL]]

        return style

    @property
    def widths(self):
        """Computes the column widths of the entire table."""
        return [
            # Width of the first column is set to accommodate the
            # longest title.
            max_width(sig.titles, 'Normal'),

            self._name_col_width(),
            None, # Signature occupies all remaining width.
            self._date_col_width(),
        ]

    def _name_col_width(self):
        """Calculates the width of the name column."""
        style = stylesheet['SignatureFieldTitle']
        title_width = stringWidth('Name', style.fontName, style.fontSize)

        # The title cell includes default left and right padding.
        title_width += DEFAULT_TABLE_HORIZ_PAD * 2

        widest = max([
            title_width,
            self._name_entry_field().wrap()[0],
        ])

        return widest + SUBSECTION_RULE_WEIGHT

    def _date_col_width(self):
        """Calculates the width of the date column."""
        style = stylesheet['SignatureFieldTitle']
        title_width = stringWidth('Date', style.fontName, style.fontSize)

        # The title cell includes default left and right padding.
        title_width += DEFAULT_TABLE_HORIZ_PAD * 2

        widest = max([
            title_width,
            self._date_entry_field().wrap()[0],
        ])

        return (
            widest
            + (SUBSECTION_RULE_WEIGHT / 2) # Left side rule.
            + (SECTION_RULE_WEIGHT / 2) # Right side rule.
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

    # Coefficient applied to the font size to calculate box height.
    HEIGHT_FACTOR = 1.2

    def __init__(self, width, style_name, tooltip=None):
        super().__init__()
        self.style = stylesheet[style_name]
        self.tooltip = tooltip
        self.width = self._calc_width(width)
        self.height = self.style.fontSize * self.HEIGHT_FACTOR

    def _calc_width(self, width):
        """Computes the horizontal size from the width argument.

        The width argument can be provided in two ways:
         - If an integer, width will the sized to hold the same character
           repeated that many times.
         - If a string, width will be sized to hold it.
        """

        # Build the template string from which width will be computed.
        try:
            template = width * 'X' # Integer width argument.
        except TypeError:
            template = width # String width argument.

        return stringWidth(
            template,
            self.style.fontName,
            self.style.fontSize,
        )

    def wrap(self, *args):
        return (self.width, self.height)

    def draw(self):
        self.canv.acroForm.textfield(
            width = self.width,
            height = self.height,
            fontName = self.style.fontName,
            fontSize = self.style.fontSize,
            borderWidth = 0,
            relative=True,
            tooltip=self.tooltip,
        )
