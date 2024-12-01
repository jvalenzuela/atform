"""PDF output generation.

This module handles processing content stored in Test() instances to
generate PDF output files with ReportLab.
"""


import itertools
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import toLength
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Frame,
    IndexingFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
)

from . import id as id_
from . import (
    acroform,
    image,
    paragraph,
    state,
)
from .textstyle import stylesheet


PAGE_SIZE = LETTER
LEFT_MARGIN = toLength("0.75 in")
RIGHT_MARGIN = LEFT_MARGIN
TOP_MARGIN = toLength("0.75 in")

# This initial value is based on the single-line footer containing the
# page number and possibly version ID; it will be increased to accommodate
# a user-provided copyright notice.
BOTTOM_MARGIN = toLength("0.5 in")


# Default left and right padding for table cells, i.e., default value for
# LEFTPADDING and RIGHTPADDING table style commands.
DEFAULT_TABLE_HORIZ_PAD = toLength("6 pt")


# Thickness of lines separating top-level sections and divisions within
# each section.
SECTION_RULE_WEIGHT = toLength("1 pt")
SUBSECTION_RULE_WEIGHT = toLength("0.5 pt")


# Color for all rules(lines).
RULE_COLOR = colors.black


# Background color for table cells containing top-level section headings.
SECTION_BACKGROUND = colors.lightsteelblue


# Background color for table cells representing divisions within a section.
SUBSECTION_BACKGROUND = colors.lightgrey


# Vertical space between each top-level section.
SECTION_SEP = toLength("5 pt")


# Vertical space allotted for the Notes section.
NOTES_AREA_SIZE = toLength("2 in")


# Text color for the draft watermark.
DRAFTMARK_COLOR = colors.Color(0, 0, 0, 0.3)


def build_path(tid, root, depth):
    """Constructs a path where a test's output PDF will be written.

    The path will consist of the root, followed by a folder per
    section number limited to depth, e.g., <root>/<x>/<y> for an ID x.y.z
    and depth 2. The final number in an ID is not translated to a folder.
    """
    folders = [root]

    # Append a folder for each section level.
    for i in range(len(tid[0:depth])):

        # Include the section number and title if the section has a title.
        try:
            section = state.section_titles[tid[:i + 1]]
            section_folder = f"{tid[i]} {section}"

        # Use only the section number if the section has no title.
        except KeyError:
            section_folder = str(tid[i])

        folders.append(section_folder)

    return os.path.join(*folders)


def max_width(
        items,
        style_name,
        left_pad=DEFAULT_TABLE_HORIZ_PAD,
        right_pad=DEFAULT_TABLE_HORIZ_PAD,
):
    """Finds the width required to hold the longest among a set of strings.

    Used to size a table column such that it can hold the content
    of all rows in that column.
    """
    style = stylesheet[style_name]
    widths = [stringWidth(i, style.fontName, style.fontSize)
              for i in items]

    # The final width includes left and right table padding.
    return max(widths) + left_pad + right_pad


class PageCount(IndexingFlowable):
    """Total page count accumulator.

    This object captures the total number of pages. It is implemented as an
    IndexingFlowable so document template multiBuild() can handle runnning
    multiple build passes to determine the total number of pages.
    """

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.last_page = 1

    def isSatisfied(self):
        """Document template multiBuild() hook to enable another build pass."""
        # The build is complete if the page number equals the cached last
        # page number.
        if self.last_page == self.doc.page:
            return True

        # Update cached last page and build again.
        self.last_page = self.doc.page
        return False

    def draw(self):
        """This flowable doesn't draw anything."""


class TestDocument:
    """This class creates a PDF for a single Test instance."""

    def __init__(self, test, root, folder_depth, version):
        self.test = test
        self.version = version

        # The full name is the combination of the test's numeric
        # identifier and title.
        self.full_name = " ".join((id_.to_string(test.id), test.title))

        self.bottom_margin = BOTTOM_MARGIN

        if state.copyright_:
            self.copyright = Paragraph(
                state.copyright_,
                stylesheet["CopyrightNotice"],
            )

            # Compute the vertical height needed to hold the copyright
            # notice when wrapped to within the document body width.
            self.copyright_height = (
                self.copyright.wrap(self._body_width, 0)[1]

                # Additional space for descenders on the bottom line.
                + stylesheet["CopyrightNotice"].fontSize * 0.25
            )

            # Enlarge the bottom margin to accommodate the copyright notice.
            self.bottom_margin += self.copyright_height

        doc = self._get_doc(root, folder_depth)
        self.page_count = PageCount(doc)
        body = [self.page_count]
        body.extend(self._build_body())
        doc.multiBuild(
            body,
            maxPasses=1, # Page count takes up to two, zero-based count.
            onFirstPage=self._on_first_page,
            onLaterPages=self._on_later_pages,
        )

    def _get_doc(self, root, folder_depth):
        """Creates the document template."""
        pdfname = self.full_name + ".pdf"
        path = build_path(self.test.id, root, folder_depth)
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, pdfname)
        return SimpleDocTemplate(
            filename,
            pagesize=PAGE_SIZE,
            leftMargin=LEFT_MARGIN,
            rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN,
            bottomMargin=self.bottom_margin,
        )

    def _on_first_page(self, canvas, doc):
        """Document template callback for the first page."""
        if self.version == "draft":
            self._draftmark(canvas, doc)

        self._footer(canvas, doc)

    def _on_later_pages(self, canvas, doc):
        """Document template callback for all pages after the first."""
        self._on_first_page(canvas, doc)
        self._header(canvas, doc)

    def _header(self, canvas, doc):
        """Draws the page header."""
        self._set_canvas_text_style(canvas, "Header")
        baseline = doc.pagesize[1] - TOP_MARGIN

        canvas.drawString(LEFT_MARGIN,
                          baseline,
                          self.full_name)

    def _footer(self, canvas, doc):
        """Draws the page footer."""
        baseline = self.bottom_margin

        # The copyright notice is placed in a dedicated frame so the text
        # can be wrapped as necessary.
        if state.copyright_:
            baseline -= self.copyright_height
            frame = Frame(
                LEFT_MARGIN,
                baseline,
                self._body_width,
                self.copyright_height,
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )
            frame.addFromList([self.copyright], canvas)

        self._set_canvas_text_style(canvas, "Footer")

        # Offset text relative to the font size.
        baseline -= stylesheet["Footer"].fontSize * 1.2

        pages = f"Page {doc.page} of {self.page_count.last_page}"
        canvas.drawCentredString(doc.pagesize[0] / 2, baseline, pages)

        # Add version information if available.
        if self.version and (self.version != "draft"):
            x = doc.pagesize[0] - RIGHT_MARGIN
            version_text = f"Document Version: {self.version}"
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
            self._title_block(),
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

    @property
    def _body_width(self):
        """Horizontal space available for body content."""
        return PAGE_SIZE[0] - LEFT_MARGIN - RIGHT_MARGIN

    def _title_block(self):
        """
        Creates title information on the top of the first page containing
        project information, test number & title, and logo. Constructed
        as a table with one row; the logo, if any, is the first column,
        and a nested table for the information fields occupies the
        second column.
        """
        rows = [[
            state.logo,
            self._title_block_fields()
        ]]

        style =[
            # Center the logo.
            ("ALIGN", (0, 0), (0, 0), "CENTER"),

            # Both the logo and fields table are vertically centered.
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),

            # Remove right padding from the fields table as it goes all
            # the way to the right margin.
            ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
        ]

        # Remove the left padding from the column containing the fields table
        # if no logo is present, allowing the fields table to abut the
        # left margin.
        if not state.logo:
            style.append(("LEFTPADDING", (1, 0), (1, 0), 0))

        # The image width is fixed to the maximum allowable logo size
        # regardless of the actual image size. If no logo is being used,
        # the image column width is set to zero.
        image_width = toLength(
            f"{image.MAX_LOGO_SIZE.width} in"
        ) if state.logo else 0

        widths = [
            image_width,

            # The fields table occupies all remaining horizontal space.
            self._body_width - image_width
        ]

        return Table(
            rows,
            style=style,
            colWidths=widths,
        )

    def _title_block_fields(self):
        """Builds a table containing the title block fields."""
        items = []

        # Add optional project information fields.
        try:
            items.append(("Project", self.test.project_info["project"]))
        except KeyError:
            pass
        try:
            items.append(("System", self.test.project_info["system"]))
        except KeyError:
            pass

        # Add test identification fields.
        items.append(("Number", id_.to_string(self.test.id)))
        items.append(("Title", self.test.title))

        # Add a colon after each field name.
        items = [(f"{i[0]}:", i[1]) for i in items]

        rows = [[
            Paragraph(title, stylesheet["HeaderRight"]),
            Paragraph(value, stylesheet["Header"]),
        ] for title, value in items]

        style = [
            # Remove horizontal padding from the field name column.
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, -1), 0),

            # Vertically align titles with the first line of each field.
            ('VALIGN', (0, 0), (0, -1), 'TOP'),
        ]

        widths = [
            max_width(
                [i[0] for i in items],
                "HeaderRight",
                left_pad=0,
                right_pad=0,
            ),

            # The value column is left unspecified as the parent title block
            # table will be stretched to fill.
            None,
        ]

        return Table(
            rows,
            style=style,
            colWidths=widths,
        )

    def _objective(self):
        """Generates Objective section."""
        if not self.test.objective:
            return None

        rows = [[paragraph.make_paragraphs(self.test.objective)]]
        return self._section("Objective", rows)

    def _references(self):
        """Generates References flowables."""
        if not self.test.references:
            return None

        # Generate a row for each reference category.
        rows = [
            [Paragraph(state.ref_titles[label], stylesheet["NormalRight"]),
             Paragraph(
                 ", ".join(self.test.references[label]),
                 stylesheet["Normal"]
             )]
            for label in self.test.references
        ]

        titles = [state.ref_titles[label] for label in self.test.references]

        column_widths = [
            # First column is sized to fit the longest category title.
            max_width(titles, "NormalRight"),

            # Second column gets all remaining space.
            None,
        ]

        # Include LEFTPADDING and RIGHTPADDING.
        column_widths[0] = column_widths[0] + (2 * DEFAULT_TABLE_HORIZ_PAD)

        table_style = [
            ("LINEBEFORE", (1, 1), (1, -1), SUBSECTION_RULE_WEIGHT, RULE_COLOR),
            ("LINEABOVE", (0, 2), (-1, -1), SUBSECTION_RULE_WEIGHT, RULE_COLOR),

            # Category column vertical alignment.
            ("VALIGN", (0, 1), (0, -1), "MIDDLE"),
        ]

        return self._section(
            "References",
            rows,
            style=table_style,
            colWidths=column_widths,
        )

    def _equipment(self):
        """Generates the Required Equipment section."""
        if not self.test.equipment:
            return None

        return self._bullet_list_section(
            "Required Equipment",
            self.test.equipment
        )

    def _preconditions(self):
        """Generates Preconditions section."""
        if not self.test.preconditions:
            return None

        return self._bullet_list_section(
            "Preconditions",
            self.test.preconditions)

    def _procedure(self):
        """Creates the Procedure section."""
        if not self.test.procedure:
            return None

        proc = ProcedureList(self.test.procedure)
        return self._section(
            "Procedure",
            proc.rows,
            style=proc.style,
            nosplit=False,
            colWidths=proc.widths,
            repeatRows=(1,),
        )

    def _notes(self):
        """Generates the Notes section."""
        return self._section("Notes", [[Spacer(0, NOTES_AREA_SIZE)]])

    def _environment(self):
        """Generates the Environment section."""
        if not self.test.fields:
            return None

        rows = [[Paragraph(f.title, stylesheet["NormalRight"]),
                 acroform.TextEntry(f.length)]
                for f in self.test.fields]

        # Field title widths for column 0.
        widths = [
            max_width(
                [f.title for f in self.test.fields],
                "NormalRight",
            ),

            # All remaining width to the text entry column.
            None,
        ]

        table_style = [
            # Horiziontal rule between each item.
            ("LINEABOVE", (0, 2), (-1, -1), SUBSECTION_RULE_WEIGHT, RULE_COLOR),
        ]

        return self._section(
            "Environment",
            rows,
            colWidths=widths,
            style=table_style,
        )

    def _approval(self):
        """Generates the Approval section."""
        if not state.signatures:
            return None

        content = Approval()
        return self._section(
            "Approval",
            content.rows,
            style=content.style,
            colWidths=content.widths,
        )

    def _section(self, title, rows, style=None, nosplit=True, **kwargs):
        """Creates a table enclosing an entire top-level section."""
        # Add the title as the first row.
        rows.insert(0, [
            Preformatted(title, stylesheet["SectionHeading"])
        ])

        if style is None:
            style = []
        style.extend([
            # Border surrounding the entire section.
            ("BOX", (0, 0), (-1, -1), SECTION_RULE_WEIGHT, RULE_COLOR),

            # Title row background.
            ("BACKGROUND", (0, 0), (0, 0), SECTION_BACKGROUND),

            # The title spans all columns.
            ("SPAN", (0, 0), (-1, 0)),
        ])

        # Keep the entire section together unless the table is
        # explicitly built to handle splitting.
        if nosplit:
            style.append(("NOSPLIT", (0, 0), (-1, -1)))

        self._set_section_table_width(kwargs)

        return Table(
            rows,
            style=style,
            spaceAfter=SECTION_SEP,
            **kwargs,
        )

    def _set_section_table_width(self, table_args):
        """
        Adjusts section table column widths to fill all available
        horizontal space.
        """
        try:
            widths = table_args["colWidths"]

        # Sections with a single column do not specify widths, so that
        # column occupies the entire width.
        except KeyError:
            table_args["colWidths"] = [self._body_width]

        # Sections with multiple columns will have one column that
        # will be streteched to occupy all remaining space.
        else:
            stretch_col = widths.index(None)
            remain = self._body_width - sum(w for w in widths if w)
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
            [ListItem(paragraph.make_paragraphs(i))],
            bulletType="bullet",
            )] for i in items]

        return self._section(title, rows)

    def _draftmark(self, canvas, doc):
        """Creates a draft watermark."""
        canvas.saveState()
        self._set_canvas_text_style(canvas, "Draftmark")

        # Translate origin to center of page.
        canvas.translate(doc.pagesize[0] / 2, doc.pagesize[1] / 2)

        canvas.rotate(45)
        canvas.setFillColor(DRAFTMARK_COLOR)

        # Offset y coordinate by half the font size because the text
        # is anchored at its baseline, not the midpoint.
        y = stylesheet["Draftmark"].fontSize / -2

        canvas.drawCentredString(0, y, "DRAFT")
        canvas.restoreState()


class ProcedureList:
    """Constructs the flowable containing the entire procedure list.

    The procedure list is built as a table, with one row per step.
    """

    # Header row text.
    HEADER_FIELDS = ["Step #", "Description", "Pass"]

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
        style = stylesheet["ProcedureTableHeading"]
        row = [Paragraph(s, style) for s in self.HEADER_FIELDS]
        self.rows.append(row)

    def _add_steps(self):
        """Adds rows for all steps."""
        step_style = stylesheet["ProcedureTableHeading"]
        for i, step in enumerate(self.steps, start=1):
            desc = self._step_body(step)
            step_num = Paragraph(str(i), step_style)
            self.rows.append([step_num, desc, acroform.Checkbox()])

    def _step_body(self, step):
        """
        Creates flowables containing all user-defined content for a single
        step, i.e., everything that goes in the Description column.
        """
        # Begin with the step instruction text.
        flowables = paragraph.make_paragraphs(step.text)

        if step.fields:
            flowables.extend(ProcedureStepFields(step.fields).flowables)

        return flowables

    def _add_last_row(self):
        """Creates the final row indicating the end of the procedure."""
        self.rows.append([
            Paragraph("End Procedure", stylesheet["ProcedureTableHeading"])
        ])

    @property
    def widths(self):
        """Computes column widths for the overall table."""
        style = "ProcedureTableHeading"

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
            acroform.Checkbox().wrap()[0] + (DEFAULT_TABLE_HORIZ_PAD * 2),
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
            ("BACKGROUND", (0, 1), (-1, 1), SUBSECTION_BACKGROUND),

            # Add a section rule above the header row. This is unnecessary
            # on the initial page, however, it's the only way to get
            # a rule on the top of following pages because the 'splitfirst'
            # index doesn't apply to repeated rows.
            ("LINEABOVE", (0, 1), (-1, 1), SECTION_RULE_WEIGHT, RULE_COLOR),

            # Do not split between the section header row and first step.
            ("NOSPLIT", (0, 0), (-1, 2)),

            # Do not split between the final step and last row.
            ("NOSPLIT", (0, -2), (0, -1)),

            # Horizontal rules between each step.
            ("LINEBELOW", (0, 2), (-1, -3), SUBSECTION_RULE_WEIGHT, RULE_COLOR),

            # Step number column
            ("VALIGN", (self.STEP_COL, 2), (self.STEP_COL, -2), "MIDDLE"),

            # Checkbox column
            ("ALIGN", (self.PASS_COL, 2), (self.PASS_COL, -2), "CENTER"),
            ("VALIGN", (self.PASS_COL, 2), (self.PASS_COL, -2), "MIDDLE"),

            # Last row shading.
            ("BACKGROUND", (0, -1), (-1, -1), SUBSECTION_BACKGROUND),

            # Last row spans all columns.
            ("SPAN", (0, -1), (-1, -1)),

            # Add a section rule at the bottom of every page break.
            (
                "LINEBELOW",
                (0, "splitlast"),
                (-1, "splitlast"),
                SECTION_RULE_WEIGHT,
                RULE_COLOR
            ),
        ]


class ProcedureStepFields:
    """Generates data entry fields for a single procedure step.

    Each field is implemented as a table with one row to permit varying
    column widths among each field.
    """

    # Vertical space between the procedure step text and data entry fields.
    FIELD_TABLE_SEP = toLength("12 pt")

    # Table column indices.
    TITLE_COL = 0
    FIELD_COL = 1
    SUFFIX_COL = 2

    def __init__(self, fields):
        self.fields = fields

        # Width of the title column for every field is set to accommodate
        # the longest title.
        self.title_col_width = max_width(
            [f.title for f in fields],
            "Normal",
            left_pad=0,
        )

    @property
    def flowables(self):
        """Generates the list of flowables to include in the parent step."""
        flowables = [Spacer(0, self.FIELD_TABLE_SEP)]
        flowables.extend([self._make_row(f) for f in self.fields])
        return flowables

    def _make_row(self, field):
        """Constructs the table representing a single field."""
        text_entry_field = acroform.TextEntry(field.length)
        row = [
            Paragraph(field.title, stylesheet["NormalRight"]),
            text_entry_field,
        ]

        # Add the optional suffix.
        if field.suffix:
            row.append(Paragraph(field.suffix, stylesheet["Normal"]))

        widths = [
            self.title_col_width,
            text_entry_field.wrap()[0],
            None,
        ]

        style = [
            # Remove left padding from the first column to keep the entire
            # set of fields left-aligned with the parent procedure step.
            # Right padding remains to separate the title from the text
            # entry field.
            ("LEFTPADDING", (self.TITLE_COL, 0), (self.TITLE_COL, -1), 0),

            # Remove all horizontal padding surrounding the text entry field.
            # Separation from adjacent columns is provided by padding in
            # those other columns.
            ("LEFTPADDING", (self.FIELD_COL, 0), (self.FIELD_COL, -1), 0),
            ("RIGHTPADDING", (self.FIELD_COL, 0), (self.FIELD_COL, -1), 0),
        ]

        return Table(
            [row],
            colWidths=widths,
            style=style,
        )


class Approval:
    """Creates table content for the approval section.

    Each signature is built with two rows; the upper row carries the
    titles above each field and the lower row is the actual data entry
    fields.
    """

    # Number of characters the name text entry fields should be sized to
    # accommodate.
    NAME_WIDTH = 12

    # Vertical distance between field names and the data entry fields.
    FIELD_TITLE_SEP = toLength("1 pt")

    # Column indices.
    TITLE_COL = 0
    NAME_COL = TITLE_COL + 1
    SIG_COL = NAME_COL + 1
    INITIAL_COL = SIG_COL + 1
    DATE_COL = INITIAL_COL + 1

    def __init__(self):
        self.rows = []
        for title in state.signatures:
            self._make_sig_rows(title)

    def _make_sig_rows(self, title):
        """Generates a row for a given signature entry."""
        field_style = stylesheet["SignatureFieldTitle"]

        # Top row has the signature and field titles.
        self.rows.append([
            Paragraph(title, stylesheet["NormalRight"]),
            Preformatted("Name", field_style),
            Preformatted("Signature", field_style),
            Preformatted("Initials", field_style),
            Preformatted("Date", field_style),
        ])

        # Lower row contains the text entry fields.
        self.rows.append([
            None, # Title column in empty in this row.
            self._name_entry_field(),
            None, # Signature column is blank.
            None, # Initial column is blank.
            self._date_entry_field(),
        ])

    def _name_entry_field(self):
        """Creates a name entry field."""
        return acroform.TextEntry(self.NAME_WIDTH)

    def _date_entry_field(self):
        """Creates a date entry field."""
        return acroform.TextEntry(
            "0000/00/00",
            "YYYY/MM/DD"
        )

    @property
    def style(self):
        """Generates style commands for the entire table."""
        style = list(itertools.chain.from_iterable(
            [self._sig_row_style(i) for i, sig in enumerate(state.signatures)]
            ))

        style.extend([
            # Vertical rules.
            (
                "LINEBEFORE",
                (self.NAME_COL, 1),
                (-1, -1),
                SUBSECTION_RULE_WEIGHT,
                RULE_COLOR
            ),

            # Remove all vertical padding around title column as it
            # spans two rows.
            ("TOPPADDING", (self.TITLE_COL, 1), (self.TITLE_COL, -1), 0),
            ("BOTTOMPADDING", (self.TITLE_COL, 1), (self.TITLE_COL, -1), 0),

            # Vertically center the title column.
            ("VALIGN", (self.TITLE_COL, 1), (self.TITLE_COL, -1), "MIDDLE"),
        ])

        return style

    def _sig_row_style(self, i):
        """Generates style commands for the two rows of a signature entry."""
        # Calculate the indices for the two rows assigned to this signature.
        upper = (i * 2) + 1
        lower = upper + 1

        style = [
            # Title column spans both upper and lower rows.
            ("SPAN", (self.TITLE_COL, upper), (self.TITLE_COL, lower)),

            # Remove vertical padding above the upper field name row.
            ("TOPPADDING", (self.NAME_COL, upper), (-1, upper), 0),

            # Set padding between the upper and lower row.
            (
                "BOTTOMPADDING",
                (self.NAME_COL, upper),
                (-1, upper),
                self.FIELD_TITLE_SEP
            ),

            # Remove padding above the entire lower row.
            ("TOPPADDING", (0, lower), (-1, lower), 0),
        ]

        last_row = i + 1 == len(state.signatures)
        if not last_row:
            # Rule below all but the last row are subsection rules.
            hrule_weight = SUBSECTION_RULE_WEIGHT

            # Horizontal rule beween each signature, except below the last
            # row because it's closed by a section rule.
            style.append((
                "LINEBELOW",
                (0, lower),
                (-1, lower),
                SUBSECTION_RULE_WEIGHT,
                RULE_COLOR
            ))
        else:
            # Rule below the last row is a section rule.
            hrule_weight = SECTION_RULE_WEIGHT

        # Adjust padding around the data entry fields(name and date).
        for col in [self.NAME_COL, self.DATE_COL]:
            # Set left padding so the entry fields abut the subsection rule
            # to the left.
            style.append((
                "LEFTPADDING",
                (col, lower),
                (col, lower),
                SUBSECTION_RULE_WEIGHT / 2
            ))

            # Set bottom padding so the fields rest on the rule below them.
            style.append((
                "BOTTOMPADDING",
                (col, lower),
                (col, lower),
                hrule_weight / 2
            ))

        return style

    @property
    def widths(self):
        """Computes the column widths of the entire table."""
        return [
            # Width of the first column is set to accommodate the
            # longest title.
            max_width(state.signatures, "Normal"),

            self._name_col_width(),
            None, # Signature occupies all remaining width.

            # The Initials column is sized to hold the title.
            max_width(["Initials"], "SignatureFieldTitle"),

            self._date_col_width(),
        ]

    def _name_col_width(self):
        """Calculates the width of the name column."""
        style = stylesheet["SignatureFieldTitle"]
        title_width = stringWidth("Name", style.fontName, style.fontSize)

        # The title cell includes default left and right padding.
        title_width += DEFAULT_TABLE_HORIZ_PAD * 2

        widest = max([
            title_width,
            self._name_entry_field().wrap()[0],
        ])

        return widest + SUBSECTION_RULE_WEIGHT

    def _date_col_width(self):
        """Calculates the width of the date column."""
        style = stylesheet["SignatureFieldTitle"]
        title_width = stringWidth("Date", style.fontName, style.fontSize)

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
