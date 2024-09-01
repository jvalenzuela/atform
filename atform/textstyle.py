# This module contains the stylesheet defining PDF text styles.
#
# All fonts are chosen from the 14 standard PDF fonts to ensure
# maximum compatibility with PDF readers, without embedding font
# encodings. Reference PDF 1.7, Adobe Systems, First Edition 2008-7-1,
# section 9.6.2.2.
#
# Use of a serifed typeface, Times Roman, as the default is per
# typographical convention, and leaves sans-serif available
# for use with setting verbatim text.


from reportlab.lib.enums import (
    TA_CENTER,
    TA_RIGHT,
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import inch


# Constant denoting the point unit of measure(1/72 inch). The unity value
# is because points are the default unit for ReportLab, so a conversion
# constant is not strictly necessary, however, this provides an explicit
# notation consistent with other units imported from reportlab.lib.units.
point = 1


stylesheet = getSampleStyleSheet()


stylesheet["Normal"].fontName = "Times-Roman"
stylesheet["Normal"].fontSize = 12 * point


stylesheet.add(ParagraphStyle(
    name="NormalCentered",
    parent=stylesheet["Normal"],
    alignment=TA_CENTER,
))


stylesheet.add(ParagraphStyle(
    name="NormalRight",
    parent=stylesheet["Normal"],
    alignment=TA_RIGHT,
))


stylesheet.add(ParagraphStyle(
    name="SectionHeading",
    parent=stylesheet["Heading3"],
    fontName="Times-Bold",
))


# Leading paragraph in a body of text.
stylesheet.add(ParagraphStyle(
    name="FirstParagraph",
    parent=stylesheet["Normal"],
))


# Any additional paragraphs in a body of text.
stylesheet.add(ParagraphStyle(
    name="NextParagraph",
    parent=stylesheet["FirstParagraph"],
    spaceBefore=4 * point,
    firstLineIndent=0.25 * inch,
))


stylesheet.add(ParagraphStyle(
    name="Header",
    parent=stylesheet["Heading2"],
    fontName="Times-Bold",
))


stylesheet.add(ParagraphStyle(
    name="Footer",
    parent=stylesheet["Normal"],
))


stylesheet.add(ParagraphStyle(
    name="ProcedureTableHeading",
    parent=stylesheet["Heading4"],
    fontName="Times-Bold",
    alignment=TA_CENTER,
))


stylesheet.add(ParagraphStyle(
    name="SignatureFieldTitle",
    parent=stylesheet["Normal"],
    fontSize=8 * point,
    leading=8 * point,
))


# textColor is not set here because it is ignored by the canvas methods
# used to draw the draft mark.
stylesheet.add(ParagraphStyle(
    name="Draftmark",
    fontName="Helvetica-Bold",
    fontSize=200 * point,
))


# Content entered into a TextEntryField.
stylesheet.add(ParagraphStyle(
    name="TextField",
    parent=stylesheet["Normal"],
    fontName="Helvetica",
))
