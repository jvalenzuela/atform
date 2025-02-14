import atform


######################################################################
# Setup
######################################################################

# This function can be used in the setup area to define the number of
# identifier fields. This example will use 3, for x.y.z numbering.
atform.set_id_depth(3)


######################################################################
# Content
######################################################################

# The atform.section() command will start a new section at a given
# level, and optionally assign it a name. This will create a new,
# level 1 section named "The First Section".
atform.section(1, title="The First Section")

# Starts a new level 2 subsection called "The First Subsection".
atform.section(2, title="The First Subsection")

atform.add_test("The First Test")  # This will be test 1.1.1.

# Additional tests will automatically increment the last field,
# so further tests will be 1.1.z.

atform.add_test("The Next Test")  # 1.1.2
atform.add_test("An Important Test")  # 1.1.3

# Begin a new, level 2 subsection, 1.2.z. Section names are optional,
# so this subsection will only bear a numeric identifier.
atform.section(2)

# Higher numbering fields are reset to 1 after atform.section(),
# so this test will be 1.2.1.
atform.add_test("Test Something Different")

# Tests here will start from 1.2.2.

# Begin a new level 1 section, 2.y.z. Levels 2 and 3 are reset to 1,
# so tests after this command will begin at 2.1.1.
atform.section(1, title="Another Section")

atform.add_test("Failure Test A")  # 2.1.1


######################################################################
# Output
######################################################################

atform.generate()
