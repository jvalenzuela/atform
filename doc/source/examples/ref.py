# ref.py

import testgen


######################################################################
# Setup
######################################################################

# testgen.add_reference_category() is used in the setup area to define
# reference categories that may appear in tests.
testgen.add_reference_category('Safety Functions', 'sf')
testgen.add_reference_category('FMEA', 'fmea')


######################################################################
# Content
######################################################################

testgen.Test('A Test With References',

             # The references argument is where references for each
             # test are specified.
             references={
                 'sf': ['SF17', 'SF24'],
                 'fmea': ['FM1.9', 'FM5.3']
             })

testgen.Test('A Test With Few References',

             # Reference categories that do not apply can be omitted.
             # Here only fmea references are relevant; there are no
             # sf references.
             references={
                 'fmea': ['FM6.8']
             })

# Tests with no references can simply omit the references parameter.
testgen.Test('A Test Without References')


######################################################################
# Output
######################################################################

testgen.generate()
