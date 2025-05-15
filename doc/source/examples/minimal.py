# Import atform package.
import atform


######################################################################
# Setup
#
# This area comes before any tests are created, and is for high-level
# configuration of the entire test collection. Here the setup area is
# empty as no configuration commands are necessary in this initial
# example.
######################################################################


######################################################################
# Content
#
# After setup, the content area is where the actual tests are defined.
# Tests will be automatically numbered in the order they appear.
######################################################################

# This will be test 1.
atform.add_test("The First Test")

# This will be test 2.
atform.add_test("The Second Test")

# This will be test 3.
atform.add_test("The Third Test")


######################################################################
# Output
#
# After all tests have been defined, the output area contains commands
# to generate the output PDFs. The if condition containing the
# atform.generate() function call is required.
######################################################################

if __name__ == "__main__":
    atform.generate()
