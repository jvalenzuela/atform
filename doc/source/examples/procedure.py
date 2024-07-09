# procedure.py

import testgen


######################################################################
# Content
######################################################################

testgen.Test('A Procedure Example',

             procedure=[
                 # Steps may be given as a string with only
                 # instructional text.
                 'This step is a simple string.',

                 # A step dictionary with only a 'text' key is the
                 # same as using a simple string.
                 {
                     'text': """
                     This step is given as a dictionary with no data
                     entry fields.
                     """
                 },

                 # A step dictionary used to add data entry fields.
                 {
                     'text': """
                     This is a step given as a dictionary that
                     includes data entry fields.
                     """,

                     # The 'fields' key is a list of data
                     # entry fields.
                     'fields':[

                          # A field with no suffix.
                         ('Error Code', 10),

                          # A field with a suffix.
                         ('Line Voltage', 5, 'VAC')
                     ]
                 }
             ])


######################################################################
# Output
######################################################################

testgen.generate()
