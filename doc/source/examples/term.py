# Python's built-in CSV module will be used to export a list of terms.
import csv

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

# begin-export-term <<< Marker comment for documentation code listing.
if __name__ == "__main__":
    atform.generate()

    # atform.get_terms() and any code generating output must occur
    # after atform.generate() and be protected by the same
    # if __name__ == "__main__" condition.
    terms = atform.get_terms()

    # Export terms and associated tests to a CSV file.
    with open("terms.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for term, tests in terms.items():
            row = [term]  # Term in the first column.
            row.extend(tests)  # Tests in columns after the term.
            writer.writerow(row)
# end-export-term <<< Marker comment for documentation code listing.
