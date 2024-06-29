# label.py


import testgen


######################################################################
# Content
######################################################################


# This test is referenced by another test.
testgen.Test('Validate A',
             label='doA' # Assign a label.
             )


testgen.Test('A Dependent Test',

             # This string contains placeholders for the two
             # other procedures.
             objective="""
             This procedure is dependent on tests $doA and $doX.
             """
             )


# This test is also referenced by another test.
testgen.Test('Validate X',
             label='doX' # Assign a label.
             )


######################################################################
# Output
######################################################################

testgen.generate()
