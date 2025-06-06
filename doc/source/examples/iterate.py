import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Setup
######################################################################


def button_test(button):
    """
    This function serves as a template for a button test procedure,
    customizing the test content for the button provided in the
    argument.
    """
    atform.add_test(
        f"{button} Button Test",
        procedure=[
            f"Press the {button} button.",
            f"Release the {button} button.",
        ],
    )


######################################################################
# Content
######################################################################

# Call the button_test() function to generate a test for each button.
button_test("Left")
button_test("Center")
button_test("Right")
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
