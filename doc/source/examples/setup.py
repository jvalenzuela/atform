import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Setup
######################################################################

# Place a logo in the title block.
atform.add_logo("python.png")

atform.add_copyright(
    """
    This function adds a copyright, confidentiality, or other
    similar notice. The copyright symbol can be included directly
    in the string, like ©, but the script file must be UTF-8
    encoded as this example is. The Python Unicode literal \u00a9
    can also be used, and does not require UTF-8 encoding.
    """
)

# Add signatures for executor and approver.
atform.add_signature("Executed By")
atform.add_signature("Approved By")
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Content
######################################################################

atform.add_test("Setup Example")


######################################################################
# Output
######################################################################

atform.generate()
