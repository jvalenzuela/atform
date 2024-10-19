# This module contains the text formatting API.


from . import error
import xml.etree.ElementTree as ElementTree


# Mapping between typeface and font parameters of format_text() to
# a (font, size) tuple used to populate intra-paragraph XML element
# attributes. The size value is optional to adjust height relative to
# normal text.
FONTS = {
    ("normal", "normal"): ("Times-Roman",),
    ("normal", "bold"): ("Times-Bold",),
    ("normal", "italic"): ("Times-Italic",),
    ("monospace", "normal"): ("Courier", 14),
    ("monospace", "bold"): ("Courier-Bold", 14),
    ("monospace", "italic"): ("Courier-Oblique", 14),
    ("sansserif", "normal"): ("Helvetica", 11),
    ("sansserif", "bold"): ("Helvetica-Bold", 11),
    ("sansserif", "italic"): ("Helvetica-Oblique", 11),
}


def allowed_format(i):
    """
    Formats a list of allowable format selectors into a string for use in
    error messages.
    """
    uniq = set([f[i] for f in FONTS])
    quoted = [f"'{s}'" for s in uniq]
    quoted.sort()
    return ", ".join(quoted[:-1]) + f", or {quoted[-1]}"


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def bullet_list(*items):
    """Creates a list of items.

    Items will be presented as an unnumbered list, in the same order they
    appear in the function's parameters. This function may not be nested to
    create nested lists.

    .. seealso:: :ref:`format`

    Args:
        *items (str): The bullet list items. This is *not* a Python list of
            items, but rather each item passed as a separate parameter.
            E.g., ``"Item 1", "Item 2"``, not ``["Item 1", "Item 2"]``.

    Returns:
        str: The entire list with embedded formatting that can be incorporated
        into strings passed to the ``objective``, ``equipment``,
        ``preconditions``, and ``procedure`` parameters of
        :py:class:`atform.Test`.
    """
    indent = 12 # Horizontal indentation in points applied to each item.

    # The character used at the beginning of each item. Chosen to be distinct
    # from the bullet used by ReportLab ListItem().
    symbol = "&diams;"

    stripped = []
    for i in items:
        try:
            item = i.strip()
        except AttributeError:
            raise error.UserScriptError(
                f"Invalid bullet list item type: {type(i).__name__}",
                "Bullet list items must be strings.",
            )
        else:
            stripped.append(item)

    bullet_items = [f"<bullet indent='{indent}'>{symbol}</bullet>{i}"
                    for i in stripped]

    # Add empty leading and trailing strings so items get surrounded by double
    # newlines by the final join(), ensuring the list is separated from
    # adjacent paragraphs.
    bullet_items.insert(0, "")
    bullet_items.append("")

    return "\n\n".join(bullet_items)


@error.exit_on_script_error
def format_text(text, typeface="normal", font="normal"):
    """Applies special formatting attributes to text.

    The returned string can be incorporated into strings passed to the
    ``objective``, ``equipment``, ``preconditions``, and ``procedure``
    parameters of :py:class:`atform.Test`.

    .. seealso:: :ref:`format`

    Args:
        text (str): The content to format.
        typeface (str, optional): Typeface name: ``"monospace"`` or
            ``"sansserif"``.
        font (str, optional): Font style: ``"bold"`` or ``"italic"``.

    Returns:
        str: The original text with embedded formatting information.
    """
    if not isinstance(text, str):
        raise error.UserScriptError(
            f"Invalid formatted text type: {text}",
            "Text to be formatted must be a string.",
        )

    typefaces = set([k[0] for k in FONTS.keys()])
    if not typeface in typefaces:
        raise error.UserScriptError(
            f"Invalid text format typeface: {typeface}",
            f"Select {allowed_format(0)} as a typeface.",
        )

    fonts = set([k[1] for k in FONTS.keys()])
    if not font in fonts:
        raise error.UserScriptError(
            f"Invalid text format font: {font}",
            f"Select {allowed_format(1)} as a font.",
        )

    font_values = FONTS[(typeface, font)]
    attrib = {"face":font_values[0]}
    try:
        attrib["size"] = str(font_values[1])
    except IndexError:
        pass

    # Enclose the string in a intra-paragraph XML markup element.
    e = ElementTree.Element("font", attrib=attrib)
    e.text = text
    return ElementTree.tostring(e, encoding="unicode")
