# This module implements the API for defining approval signatures.


from . import misc


# Signature titles, in the order they were defined.
titles = []


################################################################################
# Public API
#
# Items in this area are documented and exported for use by end users.
################################################################################


@misc.setup_only
def add_signature(title):
    """Adds an approval signature line.

    The signature entry contains title, name, signature, and date
    fields that will appear at the conclusion of every test. Signatures
    will be presented in the order they are defined.

    To illustrate, these statements will generate the following
    signature fields; the actual format may vary from what is shown here.

    ::

        testgen.add_signature('Executor')
        testgen.add_signature('Witness')


    ======== ==== ========= ====
    Title    Name Signature Date
    ======== ==== ========= ====
    Executor
    Witness
    ======== ==== ========= ====

    :param str title: A short description of the person signing.
    :raises: RuntimeError, TypeError, ValueError
    """
    if not isinstance(title, str):
        raise TypeError('Signature title must be a string.')
    stripped = title.strip()
    if not stripped:
        raise ValueError('Signature title must not be blank.')
    titles.append(stripped)
