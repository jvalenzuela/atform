# Miscellaneous unit test utilities.


import atform
from atform import label
import collections


def reset():
    """Resets the atform package back to its initial state.

    This is used because many atform modules store configuration state
    in global variables, which are only initialized when first imported,
    while unit test cases require this initial condition many times
    after a single import.
    """
    atform.content.tests = []
    atform.id.current_id = [0]
    atform.id.section_titles = {}
    atform.misc.project_info = {}
    atform.sig.titles = []
    atform.field.fields = collections.OrderedDict()
    atform.field.active_names = set()
    atform.ref.titles = {}
    label.labels = {}
