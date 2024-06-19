# button.py

# All scripts using testgen functions must import the testgen package.
# The import statement in main.py does not propagate to scripts imported
# by main.py.
import testgen


# Although not required, separate scripts typically contain their own section,
# so this command will open a new section: 1.x Buttons.
testgen.section(0, title='Buttons')


testgen.Test('The First Button Test') # This will be 1.1.
