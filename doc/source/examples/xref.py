# xref.py


# Python's built-in CSV module will be used to export a
# cross-reference file.
import csv

import testgen


######################################################################
# Setup
######################################################################

# Define a safety function reference category.
testgen.add_reference_category('Safety Functions', 'sf')


######################################################################
# Content
######################################################################

# Test 1 with several 'sf' references.
testgen.Test('Button 3',
             references={
                 'sf': ['SF7', 'SF42', 'SF99']
             })


# Test 2 with no references.
testgen.Test('Relay 66')

# Test 3 with a single 'sf' reference.
testgen.Test('Zone 4',
             references={
                 'sf': ['SF42']
             })


######################################################################
# Output
######################################################################

testgen.generate()

# Acquire all cross-references.
xrefs = testgen.get_xref()

# Export safety function cross-reference to a CSV file.
sf_refs = xrefs['sf'] # Get all references in the 'sf' category.
with open('safetyfunctions.csv', 'w', newline='') as f:
    writer = csv.writer(f)

    # Generate a row for each safety function. Dictionary keys,
    # which are safety functions in this case, are not ordered,
    # so sorted() is used here to list them in numerical order.
    for sf in sorted(sf_refs, key=lambda s: int(s[2:])):
        row = [sf] # Safety function name in the first column.

        # Append the list of tests after the safety function name.
        row.extend(sf_refs[sf])

        writer.writerow(row)
