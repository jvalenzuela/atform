# project_info.py


import testgen


######################################################################
# Setup
######################################################################

# Define the global project name for all tests. The system name
# is not assigned here; it will be defined in the Content area at the
# start of each section.
testgen.set_project_info(project='The Big Project')

# Use two-level identifiers so each system will be dedicated to
# a top-level section.
testgen.set_id_depth(2)


######################################################################
# Content
######################################################################

# Start the first section and assign the system name.
testgen.section(0, title='System A')
testgen.set_project_info(system='System A')

# These tests will be 1.x, and bear 'System A' as the system name.
testgen.Test('Button 1 Test')
testgen.Test('Button 2 Test')
testgen.Test('Button 3 Test')


# Start the next section and update the system name.
testgen.section(0, title='System B')
testgen.set_project_info(system='System B')

# These tests will be 2.x, and bear 'System B' as the system name.
testgen.Test('Switch 1 Test')
testgen.Test('Switch 2 Test')
testgen.Test('Switch 3 Test')


######################################################################
# Output
######################################################################

testgen.generate()
