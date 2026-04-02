"""Embedded object references.

This module implements a way to embed a reference to an object within
user-provided text. The process is as follows:

1. An API call creates an internal object to store some content
   intended to be embedded in user-provided text.

2. This module stores the new object by the hash of its content.

3. A reference string is generated containing the hash that is then
   returned to the user to be inserted into the user string.

4. During PDF generation, reference strings are located within the user
   strings and converted back to their original object.
"""

import hashlib
import re


objects = {}  # All stored objects keyed by hash.


def store(obj):
    """Stores an object to be embedded within user text."""
    hash_ = _calc_hash(obj)
    objects[hash_] = obj
    return f"<atform ref:{hash_}>"


def _calc_hash(obj):
    """Computes the hash value of an object to be stored."""
    person = _str_to_bytes(type(obj).__name__)
    hash_ = hashlib.blake2b(person=person)
    for field in obj.hash_fields:
        # Insert a constant separator between each field. This ensures
        # ["ab", "c"] yields a different hash from ["a", "bc"].
        hash_.update(b"\0")

        hash_.update(_str_to_bytes(field))

    return hash_.hexdigest().lower()  # Force lower-case for Resolver.re_embed.


def _str_to_bytes(s):
    """Converts a string field to bytes."""
    return bytes(s, "utf-8")


class Resolver:
    """Converts embedded references back to their original objects."""

    def __init__(self):
        # Copy the set of stored objects to be carried with this instance.
        self.objects = dict(objects)

        self.handlers = {}

        # Pattern to locate embedded references within user text,
        # essentially searching for instances of strings returned by store().
        self.re_embed = re.compile(r"<atform ref:(?P<hash>[a-f\d]{128})>")

    def register_handler(self, typ, func):
        """Registers a function to convert a given object type."""
        self.handlers[typ] = func

    def resolve(self, src):
        """Locates and converts references embedded in a string."""
        segments = []
        i = 0
        for match in self.re_embed.finditer(src):
            # Add any content before the embedded reference.
            if i != match.start():
                segments.append(src[i : match.start()])

            # Add object corresponding to the embedded reference.
            hash_ = match.group("hash")
            segments.append(self._convert(hash_))

            i = match.end()

        # Add remaining content after the final embedded reference.
        if i < len(src):
            segments.append(src[i:])

        return segments

    def _convert(self, hash_):
        """Converts a hash to the original object or handler result."""
        obj = self.objects[hash_]
        try:
            handler = self.handlers[type(obj).__name__]

        # Return original object if no handler is registered for this type.
        except KeyError:
            return obj

        return handler(obj)
