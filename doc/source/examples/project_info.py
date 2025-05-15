import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Setup
######################################################################

# Define the global project name for all tests. The system name
# is not assigned here; it will be defined in the Content area at the
# start of each section.
atform.set_project_info(project="The Big Project")

# Use two-level identifiers so each system will be dedicated to
# a top-level section.
atform.set_id_depth(2)


######################################################################
# Content
######################################################################

# Start the first section and assign the system name.
atform.section(1, title="System A")
atform.set_project_info(system="System A")

# These tests will be 1.x, and bear "System A" as the system name.
atform.add_test("Button 1 Test")
atform.add_test("Button 2 Test")
atform.add_test("Button 3 Test")


# Start the next section and update the system name.
atform.section(1, title="System B")
atform.set_project_info(system="System B")

# These tests will be 2.x, and bear "System B" as the system name.
atform.add_test("Switch 1 Test")
atform.add_test("Switch 2 Test")
atform.add_test("Switch 3 Test")
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
