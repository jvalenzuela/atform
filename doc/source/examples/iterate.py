# iterate.py


import testgen


######################################################################
# Setup
######################################################################

def button_test(button):
    """
    This function serves as a template for a button test procedure,
    customizing the test content for the button provided in the
    argument.
    """
    testgen.Test("{0} Button Test".format(button),
             procedure=[
                 "Press the {0} button.".format(button),
                 "Release the {0} button.".format(button)
             ])


######################################################################
# Content
######################################################################

# Call the button_test() function to generate a test for each button.
button_test('Left')
button_test('Center')
button_test('Right')


######################################################################
# Output
######################################################################

testgen.generate()
