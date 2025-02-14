"""Package versioning.

This module handles versioning the atform package, not the version control
interface available to end users.
"""

from . import error


# This is the version number for the entire module, and is used by the
# hatch packaging and Sphinx documentation systems.
VERSION = "0.2"


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@error.exit_on_script_error
def require_version(major, minor=0):
    """Verifies the installed version of atform.

    Aborts the script if the installed version does not match the major
    version, or is less than the minor version.

    .. seealso:: :ref:`upgrade`

    Args:
        major (int): The required major version.
        minor (int, optional): The required minor version.
    """
    if not isinstance(major, int):
        raise error.UserScriptError(
            f"Invalid major version data type: {type(major).__name__}",
            "Major version must be an integer.",
        )
    if not isinstance(minor, int):
        raise error.UserScriptError(
            f"Invalid minor version data type: {type(minor).__name__}",
            "Minor version must be an integer.",
        )
    if major < 1:
        raise error.UserScriptError(
            f"Invalid major version: {major}",
            "Major version must be greater than or equal to 1.",
        )
    if minor < 0:
        raise error.UserScriptError(
            f"Invalid minor version: {minor}",
            "Minor version must be greater than or equal to 0.",
        )
    inst_major, inst_minor = [int(x) for x in VERSION.split(".")]
    if (inst_major != major) or (inst_minor < minor):
        raise error.UserScriptError(
            f"""This script requires atform version {major}.{minor} or
            later.""",
            f"""Install atform version {major}.{minor} or greater,
            and less than {major+1}.0.""",
        )
