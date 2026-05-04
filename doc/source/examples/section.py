import atform


######################################################################
# Setup
######################################################################


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Content
######################################################################

# atform.section() will start a new section at a given level,
# and optionally assign it a name. This will create a new,
# level 1 section named "The First Section".
atform.section(1, title="The First Section")

# Start a new level 2 subsection called "The First Subsection".
atform.section(2, title="The First Subsection")

# This will be test 1.1.1. The identifier assigned to tests always
# includes the current section number plus one level to enumerate
# tests within that section.
atform.add_test("The First Test")

# Additional tests will continue in the current section,
# automatically incrementing the last field.

atform.add_test("The Next Test")  # 1.1.2
atform.add_test("An Important Test")  # 1.1.3

# Begin a new level 2 subsection, 1.2.z. Section names are optional,
# so this subsection will only bear a numeric identifier.
atform.section(2)

atform.add_test("Test Something Different")  #  1.2.1

# The resume option will continue numbering in a parent section
# without starting a new section. Tests will proceed at the next
# available number.
atform.section(1, resume=True)

atform.add_test("Failure Test A")  # 1.3
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
