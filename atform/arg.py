"""This module processes command line arguments."""

import argparse
import re
import sys

from . import state


class InvalidIdError(Exception):
    """Raised when an invalid ID or range is found in the argument list."""


def parse(args=None):
    """Top-level function for this module to process all arguments.

    Returns a list of IDs and ranges listed in the arguments. A single ID
    is presented as a tuple of integers, e.g., x.y.z is (x,y,z), and ranges
    are represented as tuple of IDs, e.g., a.b-x.y is ((a,b), (x,y)).
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "id",
        help="Test ID(s) to generate; all tests will be generated if omitted.",
        nargs="*",
    )
    ns = parser.parse_args(args)
    return parse_ids(ns.id)


def parse_ids(args):
    """Parses command line arguments into numeric IDs.

    Each ID must either be a single ID or a range consisting of two IDs
    separated by a hyphen.
    """
    # Recombine all arguments into a single string so ranges that may include spaces
    # can be normalized.
    all_args = " ".join(args)

    # Remove space surrounding hyphens so a range including a hyphen
    # is maintained within a single string when the arguments are split
    # later for parsing.
    all_args = re.sub(r"\s*-\s*", "-", all_args)

    ids = []
    for arg in all_args.split():

        # Select a parser function to parse either a single ID or an ID range.
        parser = split_range if "-" in arg else string_to_id

        try:
            id_ = parser(arg)
        except InvalidIdError as e:
            sys.exit(f"Error parsing ID '{arg}' from command line: {e}")
        ids.append(id_)

    return ids


def split_range(s):
    """Parses a string defining a range of IDs."""
    ids = s.split("-")
    if len(ids) != 2:
        raise InvalidIdError(
            "An ID range must consist of two IDs separated by a hyphen."
        )
    start = string_to_id(ids[0])
    end = string_to_id(ids[-1])
    if end <= start:
        raise InvalidIdError("The first ID in a range must be less than the second ID.")
    return (start, end)


def string_to_id(s):
    """Converts a string representation of an ID to a tuple of integers."""
    try:
        id_ = tuple(int(i) for i in s.split("."))
    except ValueError as e:
        raise InvalidIdError(
            "IDs must consist of integers separated by periods."
        ) from e

    # An ID may not have more fields than the configured identifier depth.
    max_len = len(state.current_id)
    if len(id_) > max_len:
        raise InvalidIdError(f"IDs cannot have more than {max_len} fields.")

    # All ID fields must be greater than zero.
    for i in id_:
        if i < 1:
            raise InvalidIdError("ID fields must be greater than zero.")

    return id_
