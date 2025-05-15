import atform


# begin-listing <<< Marker comment for documentation code listing.
######################################################################
# Setup
######################################################################

atform.set_id_depth(2)


######################################################################
# Content
#
# Here, import statements load content from separate scripts. The
# imported scripts must reside in the same folder as this top-level
# script, and the name given to the import statement does not
# include the .py extension.
######################################################################

import button
import switch

# Any number of import statements may follow for additional content.
# end-listing <<< Marker comment for documentation code listing.


######################################################################
# Output
#
# When a project is divided into separate scripts as demonstrated in
# this example, the atform.generate() call must be located in the
# top-level script.
######################################################################

if __name__ == "__main__":
    atform.generate()
