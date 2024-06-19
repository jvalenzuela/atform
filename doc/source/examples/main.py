# main.py

import testgen


################################################################################
# Setup
################################################################################

testgen.set_id_depth(2)


################################################################################
# Content
#
# Here, import statements load content from separate scripts. The imported
# scripts must reside n the same folder as this top-level script, and
# the name given to the import statement does not include the .py extension.
################################################################################

import button
import switch

# Any number of import statements may follow for additional content.


################################################################################
# Output
################################################################################

testgen.generate()
