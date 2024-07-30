# skip.py

import atform


######################################################################
# Setup
######################################################################

atform.set_id_depth(2)


######################################################################
# Content
######################################################################

atform.section(0, title='The First Section')

# Tests here will be numbered 1.x.

# The optional id parameter of atform.section() can be used to
# advance a level to a specific value instead of just incrementing.
# Here the level 0 field will be advanced to 5 instead of 2, reserving
# sections 2.x, 3.x, and 4.x.
atform.section(0, id=5, title='A Later Section')

atform.Test('An Important Test') # This will be 5.1.

# The atform.skip_test() function can advance the last field in a
# test number. Without any arguments it will skip a single number,
# which can be useful when removing a test. This example will
# skip 5.2.
atform.skip_test()

atform.Test('Verify Something') # This will be 5.3.

# atform.skip_test() can also jump to a specific value, instead of
# skipping a single test.
atform.skip_test(10)

atform.Test('Verify Another') # This will be 5.10.


######################################################################
# Output
######################################################################

atform.generate()
