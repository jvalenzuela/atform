# This module contains the text formatting API.


import xml.etree.ElementTree as ElementTree


# Mapping between typeface and font parameters of format_text() to
# a (font, size) tuple used to populate intra-paragraph XML element
# attributes. The size value is optional to adjust height relative to
# normal text.
FONTS = {
    ('normal', 'normal'): ('Times-Roman',),
    ('normal', 'bold'): ('Times-Bold',),
    ('normal', 'italic'): ('Times-Italic',),
    ('monospace', 'normal'): ('Courier', 14),
    ('monospace', 'bold'): ('Courier-Bold', 14),
    ('monospace', 'italic'): ('Courier-Oblique', 14),
    ('sansserif', 'normal'): ('Helvetica', 11),
    ('sansserif', 'bold'): ('Helvetica-Bold', 11),
    ('sansserif', 'italic'): ('Helvetica-Oblique', 11),
}


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


def format_text(text, typeface='normal', font='normal'):
    """Applies special formatting attributes to text.

    The returned string can be incorporated into strings passed to the
    ``objective``, ``equipment``, ``preconditions``, and ``procedure``
    parameters of :py:func:`testgen.Test`.

    .. seealso:: :ref:`format`

    :param str text: The content to format.
    :param str typeface: Optional typeface name: ``'monospace'`` or
                         ``'sansserif'``.
    :param str font: Optional font style: ``'bold'`` or ``'italic'``.
    :return str: A string containing the original text with embedded formatting
                 information.
    :raises: KeyError, TypeError
    """
    if not isinstance(text, str):
        raise TypeError('text must be a string.')

    typefaces = set([k[0] for k in FONTS.keys()])
    if not typeface in typefaces:
        raise KeyError(
            "Invalid typeface: '{0}'. Valid typefaces are {1}.".format(
                typeface, ', '.join(typefaces)))

    fonts = set([k[1] for k in FONTS.keys()])
    if not font in fonts:
        raise KeyError("Invalid font: '{0}'. Valid fonts are {1}.".format(
            font, ', '.join(fonts)))

    font_values = FONTS[(typeface, font)]
    attrib = {'face':font_values[0]}
    try:
        attrib['size'] = str(font_values[1])
    except IndexError:
        pass

    # Enclose the string in a intra-paragraph XML markup element.
    e = ElementTree.Element('font', attrib=attrib)
    e.text = text
    return ElementTree.tostring(e, encoding='unicode')
