import atform


######################################################################
# Setup
######################################################################

# begin-listing <<< Marker comment for documentation code listing.
# Common notices can be stored in a variable for repeated use.
WARNING = atform.notice("W001", "A common warning.")


######################################################################
# Content
######################################################################

atform.add_test(
    "Notice Example",
    procedure=[
        # A notice may be added to text with the plus operator.
        "A step with a notice." + atform.notice("M001", "A notice."),
        # Notices may also be inserted using Python's f-strings;
        # note the f preceeding the opening quotation mark and
        # the curly braces surrounding the variable name.
        f"A step including the common warning. {WARNING}",
    ],
)
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
