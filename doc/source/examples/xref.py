# Python's built-in CSV module will be used to export a
# cross-reference file.
import csv

import atform


######################################################################
# Setup
######################################################################

# Define a safety function reference category.
atform.add_reference_category("Safety Functions", "sf")


######################################################################
# Content
######################################################################

# Test 1 with several "sf" references.
atform.add_test(
    "Button 3",
    references={"sf": ["SF7", "SF42", "SF99"]},
)

# Test 2 with no references.
atform.add_test("Relay 66")

# Test 3 with a single "sf" reference.
atform.add_test(
    "Zone 4",
    references={"sf": ["SF42"]},
)


######################################################################
# Output
######################################################################

atform.generate()

# Acquire all cross-references.
xrefs = atform.get_xref()

# Export safety function cross-reference to a CSV file.
sf_refs = xrefs["sf"]  # Get all references in the "sf" category.
with open("sf-xref.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)

    # Generate a row for each safety function. Dictionary keys,
    # which are safety functions in this case, are not ordered,
    # so sorted() is used here to list them in numerical order.
    for sf in sorted(sf_refs, key=lambda s: int(s[2:])):
        row = [sf]  # Safety function name in the first column.

        # Append the list of tests after the safety function name.
        row.extend(sf_refs[sf])

        writer.writerow(row)
