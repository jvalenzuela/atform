import atform


######################################################################
# Content
######################################################################


# begin-listing <<< Marker comment for documentation code listing.
# This test is referenced by another test.
atform.add_test(
    "Validate A",
    label="doA",  # Assign a label.
)


atform.add_test(
    "A Dependent Test",
    # The objective has placeholders for the two other procedures.
    objective="This procedure is dependent on tests $doA and $doX.",
    procedure=[
        # Create a labeled procedure step.
        {
            "label": "ps_label",
            "text": "Verify something important.",
        },
        "Repeat step $ps_label.",  # Reference the labeled step.
    ],
)


# This test is also referenced by another test.
atform.add_test(
    "Validate X",
    label="doX",  # Assign a label.
    # The same procedure step label from the previous test,
    # ps_label, is reused here, yet the labels remain independent
    # because procedure step labels are local to each test.
    procedure=[
        "Refer to step $ps_label.",
        {
            "label": "ps_label",
            "text": "The labeled step.",
        },
    ],
)
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
