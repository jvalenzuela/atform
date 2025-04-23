"""Package public API definition.

This module imports all public API objects so they are accessible from the
atform namespace.
"""

from atform.addtest import (
    add_test,
)

from atform.field import (
    add_field,
    set_active_fields,
)

from atform.format import (
    bullet_list,
    format_text,
)

from atform.gen import (
    generate,
)

from atform.id import (
    section,
    set_id_depth,
    skip_test,
)

from atform.image import (
    add_logo,
)

from atform.meta import (
    list_tests,
)

from atform.misc import (
    add_copyright,
    set_project_info,
)

from atform.ref import (
    add_reference_category,
    get_xref,
)

from atform.sig import (
    add_signature,
)

from atform.term import (
    add_term,
)

from atform.version import (
    require_version,
)
