import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Setup
######################################################################

# Create fields to enter software version and IP address.
atform.add_field("Software Version", 10, "ver")
atform.add_field("IP Address", 10, "ip")

# This field will not appear on any tests until explicitly enabled.
atform.add_field("Machine Number", 3, "machine", active=False)


######################################################################
# Content
######################################################################

# This will have the "Software Version" and "IP Address" fields.
atform.add_test("Function A")

# This test excludes the "Software Version" field, so it will only
# have the "IP Address" field.
atform.add_test("Function B", exclude_fields=["ver"])

# Change the fields applied to any further tests.
atform.set_active_fields(active=["machine"])

# This test will only have a "Machine Number" field.
atform.add_test("Function C")
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
