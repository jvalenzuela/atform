import atform


######################################################################
# Content
######################################################################

# begin-listing <<< Marker comment for documentation code listing.
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
            an image and data entry fields.
            """,
            "image": "python.jpg",
            "fields": [  # The "fields" key adds data entry fields.
                ("Error Code", 10),  # A field with no suffix.
                ("Line Voltage", 5, "VAC"),  # A field with a suffix.
            ],
        },
    ],
)
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

atform.generate()
