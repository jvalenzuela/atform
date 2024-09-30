import atform


######################################################################
# Setup
######################################################################

# Define a variable to hold the common content, which is then used in
# the procedure lists. The capitalized variable name is by convention,
# not requirement.
RESET_STEP = "Do something important to try and reset."


######################################################################
# Content
######################################################################


atform.Test("The First Test",

            procedure=[
                "Perform some initial setup.",
                "Create a problem.",
                RESET_STEP,
                "Validate some response."
            ])


atform.Test("The Second Test",

            procedure=[
                "Do the setup again.",
                "Create a different problem.",
                RESET_STEP,
                "Validate another response."
            ])


######################################################################
# Output
######################################################################

atform.generate()
