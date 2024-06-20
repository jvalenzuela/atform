# setup.py

import testgen


################################################################################
# Setup
################################################################################

# Create some fields to enter software version and system name.
testgen.add_field('Software Version', 20)
testgen.add_field('System Name', 10)

# Add signatures for executor and approver.
testgen.add_signature('Executed By')
testgen.add_signature('Approved By')


################################################################################
# Content
################################################################################

testgen.Test('Setup Example')


################################################################################
# Output
################################################################################

testgen.generate()
