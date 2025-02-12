"""Package public API definition.

This module imports all public API objects so they are accessible from the
atform namespace.
"""

from atform.addtest import (
    add_test,
)

from atform.content import (
    generate,
)

from atform.field import (
    add_field,
    set_active_fields,
)

from atform.format import (
    bullet_list,
    format_text,
)

from atform.id import (
    section,
    set_id_depth,
    skip_test,
)

from atform.image import (
    add_logo,
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

from atform.version import (
    require_version,
)
