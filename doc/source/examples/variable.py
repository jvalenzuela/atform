import atform


# begin-listing <<< Marker comment for documentation code listing.
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


atform.add_test(
    "The First Test",
    procedure=[
        "Perform some initial setup.",
        "Create a problem.",
        RESET_STEP,
        "Validate some response.",
    ],
)


atform.add_test(
    "The Second Test",
    procedure=[
        "Do the setup again.",
        "Create a different problem.",
        RESET_STEP,
        "Validate another response.",
    ],
)
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
