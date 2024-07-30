# setup.py

import atform


######################################################################
# Setup
######################################################################

# Create some fields to enter software version and system name.
atform.add_field('Software Version', 20)
atform.add_field('System Name', 10)

# Add signatures for executor and approver.
atform.add_signature('Executed By')
atform.add_signature('Approved By')


######################################################################
# Content
######################################################################

atform.Test('Setup Example')


######################################################################
# Output
######################################################################

atform.generate()
