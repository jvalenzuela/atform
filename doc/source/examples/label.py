import atform


######################################################################
# Content
######################################################################


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
            "label": "ps_verify",
            "text": "Verify something important.",
        },
        "Repeat step $ps_verify.",  # Reference the labeled step.
    ],
)


# This test is also referenced by another test.
atform.add_test(
    "Validate X",
    label="doX",  # Assign a label.
)


######################################################################
# Output
######################################################################

atform.generate()
