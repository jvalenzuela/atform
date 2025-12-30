"""Unit tests for the search GUI panel."""

import string
import unittest
from unittest.mock import patch

from atform.gui import search, searchwidget
from .. import utils


def click_add_button(parent):
    """Simulates clicking the add button."""
    utils.click_button(parent, "Add Matching Tests To Build")


@patch("atform.gui.searchwidget.buildlist.add", autospec=True)
@patch("atform.gui.searchwidget.search.TestContentSearch", autospec=True)
class QueryString(unittest.TestCase):
    """Query string tests."""

    def test_empty(self, mock_search, *_mocks):
        """Confirm no search with an empty query string."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "")
        click_add_button(parent)
        mock_search().search.assert_not_called()

    def test_blank(self, mock_search, *_mocks):
        """Confirm no search with a query string containing only whitespace."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, string.whitespace)
        click_add_button(parent)
        mock_search().search.assert_not_called()

    def test_non_blank(self, mock_search, *_mocks):
        """Confirm a non-blank query string is passed to the search."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo bar")
        click_add_button(parent)
        mock_search().search.assert_called_once()
        self.assertEqual("foo bar", mock_search().search.call_args.args[0])


@patch("atform.gui.searchwidget.buildlist.add", autospec=True)
@patch("atform.gui.searchwidget.search.TestContentSearch", autospec=True)
class BuildList(unittest.TestCase):
    """Tests for search results added to the build list."""

    def test_match(self, mock_search, mock_build):
        """Confirm match sets are added to the build list."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        for result in [set(), {(1,)}, {(1,), (2,)}]:
            mock_search().search.return_value = result
            mock_build.reset_mock()
            click_add_button(parent)
            with self.subTest(result=result):
                mock_build.assert_called_once_with(result)


@patch("atform.gui.searchwidget.buildlist.add", autospec=True)
@patch("atform.gui.searchwidget.search.TestContentSearch", autospec=True)
class MatchAnyAll(unittest.TestCase):
    """Tests for the match any/all selection."""

    def test_select(self, mock_search, *_mocks):
        """Confirm selection is passed to the correct search parameter."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        for select in ["all", "any"]:
            mock_search().search.reset_mock()
            utils.click_button(parent, f"Match {select}")
            click_add_button(parent)
            with self.subTest(select=select):
                mock_search().search.assert_called_once()
                if select == "all":
                    expected = search.Grouping.ALL
                else:
                    expected = search.Grouping.ANY
                self.assertEqual(expected, mock_search().search.call_args.args[2])


@patch("atform.gui.searchwidget.buildlist.add", autospec=True)
@patch("atform.gui.searchwidget.search.TestContentSearch", autospec=True)
class CaseSensitive(unittest.TestCase):
    """Tests for the case-sensitive option."""

    def test_default(self, mock_search, *_mocks):
        """Confirm the default selection is case-insensitive."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        click_add_button(parent)
        self.assertEqual(False, mock_search().search.call_args.args[3])

    def test_select(self, mock_search, *_mocks):
        """Confirm selection is passed to the correct search parameter."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        for select in [True, False]:
            mock_search().search.reset_mock()
            utils.set_checkbox(parent, "Case-sensitive", select)
            click_add_button(parent)
            with self.subTest(select=select):
                mock_search().search.assert_called_once()
                self.assertEqual(select, mock_search().search.call_args.args[3])


@patch("atform.gui.searchwidget.buildlist.add", autospec=True)
@patch("atform.gui.searchwidget.search.TestContentSearch", autospec=True)
class Section(unittest.TestCase):
    """Tests for the section selection checkboxes."""

    SECTIONS = [
        "Title",
        "Objective",
        "References",
        "Environment",
        "Equipment",
        "Preconditions",
        "Procedure",
    ]

    def test_none(self, mock_search, *_mocks):
        """Confirm no search if no sections are selected."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        for section in self.SECTIONS:
            utils.set_checkbox(parent, section, False)
        click_add_button(parent)
        mock_search().search.assert_not_called()

    def test_single(self, mock_search, *_mocks):
        """Confirm each section is passed to the search."""
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        for section in self.SECTIONS:
            mock_search().search.reset_mock()
            for s in self.SECTIONS:
                utils.set_checkbox(parent, s, s == section)
            click_add_button(parent)
            with self.subTest(section=section):
                mock_search().search.assert_called_once()
                self.assertEqual({section}, mock_search().search.call_args.args[1])

    def test_multiple(self, mock_search, *_mocks):
        """Confirm multiple selected sections are passed to the search.

        This also serves to ensure all sections are checked by default.
        """
        parent = searchwidget.Search(None)
        utils.set_entry_text(parent, "foo")
        click_add_button(parent)
        mock_search().search.assert_called_once()
        self.assertEqual(set(self.SECTIONS), mock_search().search.call_args.args[1])
