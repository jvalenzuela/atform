# setup.py

import atform


######################################################################
# Setup
######################################################################

# Place a logo in the title block.
atform.add_logo("python.jpg")

atform.add_copyright(
    """
    This function adds a copyright, confidentiality, or other
    similar notice. The copyright symbol can be included directly
    in the string, like ©, but the script file must be UTF-8
    encoded as this example is. The Python Unicode literal \u00a9
    can also be used, and does not require UTF-8 encoding.
    """
    )

# Create some fields to enter software version and system name.
atform.add_field("Software Version", 20, "ver")
atform.add_field("System Name", 10, "sys")

# This field will not appear on any tests until explicitly enabled.
atform.add_field("Machine Number", 3, "machine", active=False)

# Add signatures for executor and approver.
atform.add_signature("Executed By")
atform.add_signature("Approved By")


######################################################################
# Content
######################################################################

# This will have the "Software Version" and "System Name" fields.
atform.Test("Function A")

# This test excludes the "Software Version" field, so it will only
# have the "System Name" field.
atform.Test("Function B",
            exclude_fields=["ver"]
            )

# Change the fields applied to any further tests.
atform.set_active_fields(active=["machine"])

# This test will only have a "Machine Number" field.
atform.Test("Function C")


######################################################################
# Output
######################################################################

atform.generate()
