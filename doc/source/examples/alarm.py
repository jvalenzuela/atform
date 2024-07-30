# alarm.py


import atform

# Import Python's built-in CSV module to read the external alarm file.
import csv


######################################################################
# Alarms
######################################################################

# Load alarms.csv using the Python csv module, creating a dictionary
# mapping alarm number to its respective message, so the text for
# any alarm can be acquired by alarms[num].
with open('alarms.csv', newline='') as f:
    reader = csv.reader(f)
    alarms = dict([(int(row[0]), row[1]) for row in reader])


def verify_alarm(num):
    """
    This function will generate a procedure step(a string) verifying
    a specific alarm based on the alarm number, which is used to
    construct a string containing the full message text.
    """
    return f"Verify the following alarm:\n\n{num}: {alarms[num]}"


######################################################################
# Content
######################################################################

# Tests use the verify_alarm() function within their procedure
# argument to include a step verifying an alarm with the message
# text acquired from the external CSV file.

atform.Test('Test Alarm 42',
            procedure=[
                "Verify normal operation.",
                "Introduce some fault condition.",
                verify_alarm(42)
            ])


atform.Test('Test Alarm 15',
            procedure=[
                "Verify normal operation.",
                "Introduce some fault condition.",
                verify_alarm(15)
            ])


atform.Test('Test Alarm 99',
            procedure=[
                "Verify normal operation.",
                "Introduce some fault condition.",
                verify_alarm(99)
            ])


######################################################################
# Output
######################################################################

atform.generate()
