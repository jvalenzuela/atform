import atform


######################################################################
# Content
######################################################################

atform.add_test(
    "A Procedure Example",
    procedure=[
        "This step is a simple string.",
        {
            "text": """
            This step is given as a dictionary with only a "text"
            key, which is equivalent to using a string.
            """
        },
        {
            "text": """
            This is a step given as a dictionary that includes
            data entry fields.
            """,
            "fields": [  # The "fields" key adds data entry fields.
                ("Error Code", 10),  # A field with no suffix.
                ("Line Voltage", 5, "VAC"),  # A field with a suffix.
            ],
        },
    ],
)


######################################################################
# Output
######################################################################

atform.generate()
