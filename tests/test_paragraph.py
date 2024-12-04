# Unit tests for the paragraph module.


import unittest

import atform


class SplitParagraphs(unittest.TestCase):
    """Unit tests for the split_paragraphs() function."""

    def test_single_LF(self):
        """Confirm lines separated by a single newline are not split."""
        self.assert_result("foo bar\nspam eggs", ["foo bar spam eggs"])

    def test_single_CRLF(self):
        """Confirm lines separated by a single CRLF are not split."""
        self.assert_result("foo bar\r\nspam eggs", ["foo bar spam eggs"])

    def test_two_LF(self):
        """Confirm lines separated by two newlines are split."""
        self.assert_result("foo bar\n\nspam eggs", ["foo bar", "spam eggs"])

    def test_two_CRLF(self):
        """Confirm lines separated by two CRLF are split."""
        self.assert_result("foo bar\r\n\r\nspam eggs", ["foo bar", "spam eggs"])

    def test_multiple_LF(self):
        """Confirm lines separated by more than two newlines are split."""
        self.assert_result("foo bar\n\n\nspam eggs", ["foo bar", "spam eggs"])

    def test_multiple_CRLF(self):
        """Confirm lines separated by more than two CRLFs are split."""
        self.assert_result("foo bar\r\n\r\n\r\nspam eggs",
                           ["foo bar", "spam eggs"])

    def test_leading_LF(self):
        """Confirm leading newlines do not create blank paragraphs."""
        self.assert_result("\n\nfoo bar", ["foo bar"])

    def test_leading_CRLF(self):
        """Confirm leading CRLFs do not create blank paragraphs."""
        self.assert_result("\r\n\r\nfoo bar", ["foo bar"])

    def test_trailing_LF(self):
        """Confirm trailing newlines do not create blank paragraphs."""
        self.assert_result("foo bar\n\n", ["foo bar"])

    def test_trailing_CRLF(self):
        """Confirm trailing CRLFs do not create blank paragraphs."""
        self.assert_result("foo bar\r\n\r\n", ["foo bar"])

    def test_whitespace_between_LF(self):
        """Confirm intervening whitespace between newlines is ignored."""
        self.assert_result("foo bar\n \t\nspam eggs",
                           ["foo bar", "spam eggs"])

    def test_whitespace_between_CRLF(self):
        """Confirm intervening whitespace between CRLFs is ignored."""
        self.assert_result("foo bar\r\n \t\r\nspam eggs",
                           ["foo bar", "spam eggs"])

    def assert_result(self, raw, expected):
        """Asserts a given string is split into expected paragraphs."""
        paras = atform.pdf.paragraph.split_paragraphs(raw)
        self.assertEqual(expected, paras)
