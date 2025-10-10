"""Backend for searching test content.

Searching is done with the whoosh module. Content from all tests is
indexed upon initialization, then searches can be dispatched from the GUI.
"""

from typing import Iterable

import whoosh.analysis  # type: ignore[import-untyped]
import whoosh.fields  # type: ignore[import-untyped]
import whoosh.filedb.filestore  # type: ignore[import-untyped]
import whoosh.qparser  # type: ignore[import-untyped]

from ..addtest import TestContent, Reference
from ..id import IdType
from ..procedure import Step
from .. import state


class CaseFolder(whoosh.analysis.Filter):
    """Filter to normalize case during indexing.

    Used in analyzers to produce content for case-insensitive searches.
    """

    def __call__(self, tokens):
        for t in tokens:
            t.text = t.text.casefold()
            yield t


# Schema field types for case-sensitive(verbatim) searching, and
# case-insensitive(casefold) searching.
VERBATIM_FIELD = whoosh.fields.TEXT(analyzer=whoosh.analysis.RegexTokenizer())
CASEFOLD_FIELD = whoosh.fields.TEXT(
    analyzer=whoosh.analysis.RegexTokenizer() | CaseFolder()
)


# Test document section names, which serve as the base for indexed schema
# field names; this also defines the listing order of GUI section checkboxes.
SECTIONS = [
    "Title",
    "Objective",
    "References",
    "Environment",
    "Equipment",
    "Preconditions",
    "Procedure",
]


# Two indexed schema fields are defined for each each test section:
# <section>_verbatim with original text for case-sensitive searches.
# <section>_casefold with casefolded text for case-insensitive searches.
INDEXED_FIELDS = {f"{sec}_verbatim": VERBATIM_FIELD for sec in SECTIONS}
INDEXED_FIELDS.update({f"{sec}_casefold": CASEFOLD_FIELD for sec in SECTIONS})


SCHEMA = whoosh.fields.Schema(id=whoosh.fields.STORED, **INDEXED_FIELDS)


class TestContentSearch:
    """
    This object houses the search index of all test content and provides
    an interface for finding matching terms.
    """

    # This object is implemented as class as it requires internal state,
    # namely the index, and requires only a single public method.
    # pylint: disable=too-few-public-methods

    # Match any/all selection mapping.
    COMBINE_GROUP = {
        "all": whoosh.qparser.AndGroup,
        "any": whoosh.qparser.OrGroup,
    }

    def __init__(self):
        storage = whoosh.filedb.filestore.RamStorage()
        self.index = storage.create_index(SCHEMA)
        writer = self.index.writer()

        for test in state.tests.values():
            fields = index_test(test)

            verbatim = {f"{key}_verbatim": value for key, value in fields.items()}
            writer.add_document(id=test.id, **verbatim)

            casefold = {
                f"{key}_casefold": value.casefold() for key, value in fields.items()
            }
            writer.add_document(id=test.id, **casefold)

        writer.commit()

    def search(self, text, sections, combine, match_case):
        """Executes a search for a given query text."""
        if match_case:
            field_suffix = "verbatim"
        else:
            field_suffix = "casefold"
        parser = whoosh.qparser.MultifieldParser(
            [f"{name}_{field_suffix}" for name in sections],
            self.index.schema,
            group=self.COMBINE_GROUP[combine],
        )
        query = parser.parse(text)
        with self.index.searcher() as searcher:
            results = searcher.search(query, limit=None)
            matches = {r["id"] for r in results}
        return matches


def index_test(test: TestContent) -> dict[str, str]:
    """Creates index fields from a test's content."""
    fields = {"Title": test.title}
    if test.objective:
        fields["Objective"] = test.objective
    fields["References"] = index_refs(test.references)
    fields["Environment"] = "\n".join(f.title for f in test.fields)
    fields["Equipment"] = "\n".join(test.equipment)
    fields["Preconditions"] = "\n".join(test.preconditions)
    fields["Procedure"] = index_procedure(test.procedure)
    return fields


def index_refs(refs: list[Reference]) -> str:
    """Converts a test's references into a single string for indexing."""
    items = []
    for r in refs:
        items.append(r.title)
        items.extend(r.items)
    return "\n".join(items)


def index_procedure(steps: list[Step]) -> str:
    """Converts a test's procedure list into a single string for indexing."""
    items = []
    for step in steps:
        items.append(step.text)
        for field in step.fields:
            items.append(field.title)
            if field.suffix:
                items.append(field.suffix)
    return "\n".join(items)
