import csv
import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Content
######################################################################

atform.add_test("The First Test")
atform.add_test("Another Test")
atform.add_test("The Last Test")


######################################################################
# Output
######################################################################

if __name__ == "__main__":
    atform.generate()

    # Export IDs and titles of all tests to a CSV file.
    with open("tests.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(atform.list_tests())
