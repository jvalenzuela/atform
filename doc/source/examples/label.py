import atform


######################################################################
# Content
######################################################################


# This test is referenced by another test.
atform.add_test("Validate A",
                label="doA" # Assign a label.
                )


atform.add_test("A Dependent Test",

                # This string contains placeholders for the two
                # other procedures.
                objective="""
                This procedure is dependent on tests $doA and $doX.
                """,

                procedure=[
                    # Create a labeled procedure step.
                    {
                        "label":"ps_verify",
                        "text":"Verify something important."
                    },

                    # Reference the labeled procedure step.
                    "Repeat step $ps_verify."
                ])


# This test is also referenced by another test.
atform.add_test("Validate X",
                label="doX" # Assign a label.
                )


######################################################################
# Output
######################################################################

atform.generate()
