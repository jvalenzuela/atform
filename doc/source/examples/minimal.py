# minimal.py


# Import testgen package.
import testgen


################################################################################
# Setup
#
# This area comes before any tests are created, and is for high-level
# configuration of the entire test collection. Here the setup area is empty
# as no configuration commands are necessary in this initial example.
################################################################################


################################################################################
# Content
#
# After setup, the content area is where the actual tests are defined. Tests
# will be automatically numbered in the order they appear.
################################################################################

# This will be test 1.
testgen.Test('The First Test')

# This will be test 2.
testgen.Test('The Second Test')

# This will be test 3.
testgen.Test('The Third Test')


################################################################################
# Output
#
# After all tests have been defined, the output area contains commands to
# generate the output PDFs.
################################################################################

testgen.generate()
