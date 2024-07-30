# Module versioning, not the version control interface.


# This is the version number for the entire module, and is used by the
# hatch packaging and Sphinx documentation systems.
VERSION = '0.0'


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


def require_version(major, minor=0):
    """Verifies the installed version of testgen.

    Aborts the script if the installed version does not match the major
    version, or is less than the minor version.

    Args:
        major (int): The required major version.
        minor (int, optional): The required minor version.

    Raises:
        SystemExit
        TypeError
        ValueError
    """
    if not isinstance(major, int):
        raise TypeError('Major version must be an integer.')
    if not isinstance(minor, int):
        raise TypeError('Minor version must be an integer.')
    if major < 1:
        raise ValueError('Major version must be greater than or equal to 1.')
    if minor < 0:
        raise ValueError('Minor version must be greater than or equal to 0.')
    inst_major, inst_minor = [int(x) for x in VERSION.split('.')]
    if (inst_major != major) or (inst_minor < minor):
        module_name = __name__.split('.')[0]
        raise SystemExit(
            "This script requires {0} major version {1} and at least minor "
            "version {2}, i.e., {1}.{2} or greater, and less than "
            "{3}.0.".format(
                module_name,
                major,
                minor,
                major+1,
            ))
