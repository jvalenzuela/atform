# section.py

import testgen


######################################################################
# Setup
######################################################################

# This function can be used in the setup area to define the number of
# identifier fields. This example will use 3, for x.y.z numbering.
testgen.set_id_depth(3)


######################################################################
# Content
######################################################################

# The testgen.section() command will start a new section at a given
# level, and optionally assign it a name. This will create a new,
# level 0 section named 'The First Section'.
testgen.section(0, title='The First Section')

# Starts a new level 1 subsection called 'The First Subsection'.
testgen.section(1, title='The First Subsection')

testgen.Test('The First Test') # This will be test 1.1.1.

# Additional tests will automatically increment the last field,
# so further tests will be 1.1.z.

testgen.Test('The Next Test') # 1.1.2
testgen.Test('An Important Test') # 1.1.3

# Begin a new, level 1 subsection, 1.2.z. Section names are optional,
# so this subsection will only bear a numeric identifier.
testgen.section(1)

# Higher numbering fields are reset to 1 after testgen.section(),
# so this test will be 1.2.1.
testgen.Test('Test Something Different')

# Tests here will start from 1.2.2.

# Begin a new level 0 section, 2.y.z. Levels 1 and 2 are reset to 1,
# so tests after this command will begin at 2.1.1.
testgen.section(0, title='Another Section')

testgen.Test('Failure Test A') # 2.1.1

# The id parameter can be used to jump to a specific section number,
# instead of incrementing to the next number. This command advances
# the level 1 field to 5, so the tests will begin at 2.5.1.
testgen.section(1, id=5)

testgen.Test('Functional Test G') # 2.5.1


######################################################################
# Output
######################################################################

testgen.generate()
