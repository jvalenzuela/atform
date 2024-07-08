# format.py


import testgen


######################################################################
# Content
######################################################################

testgen.Test('Formatting',

             objective="""
             This objective is defined with a
             triple-quoted string broken across several lines;
             a common Python idiom for handling long strings.
             However, it will be formatted appropriately in the
             output PDF.

             This next paragraph is separated from the previous
             by one or more blank lines. Another sample of how
             spacing in the input strings does not impact the
             output are the precondition items, which contain
             the same sentence with varying spacing
             and line breaks, yet are all rendered identically
             in the PDF.
             """,

             preconditions=[
                 "The quick brown fox jumps over the lazy dog.",

                 """The     quick     brown     fox     jumps
                    over    the       lazy      dog.""",

                 """The quick brown fox
                 jumps over the lazy dog."""
             ])


######################################################################
# Output
######################################################################

testgen.generate()
