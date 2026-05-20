import atform


######################################################################
# Setup
######################################################################

# begin-add-term <<< Marker comment for documentation code listing.
atform.add_term("foo42", "myTerm", typeface="sansserif", font="bold")
# end-add-term <<< Marker comment for documentation code listing.


######################################################################
# Content
######################################################################

# begin-use-term <<< Marker comment for documentation code listing.
atform.add_test(
    "A Test Using A Term",
    objective="This test uses $myTerm.",
    procedure=[
        "Exercise the system.",
        "Verify the state of $myTerm.",
    ],
)
# end-use-term <<< Marker comment for documentation code listing.

# begin-support-term <<< Marker comment for documentation code listing.
atform.add_test(
    "A Supporting Test",
    supports_terms=["myTerm"],
    objective="This test supports $myTerm.",
    procedure=[
        "Verify the state of $myTerm.",
        "Verify behavior resulting from the state of $myTerm",
    ],
)
# end-support-term <<< Marker comment for documentation code listing.


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()
