# Units tests for the PDF module.


from tests import utils
import atform.id
import atform.pdf
import os
import unittest


class SplitParagraphs(unittest.TestCase):
    """Unit tests for the split_paragraphs() function."""

    def test_single_LF(self):
        """Confirm lines separated by a single newline are not split."""
        self.assert_result('foo bar\nspam eggs', ['foo bar spam eggs'])

    def test_single_CRLF(self):
        """Confirm lines separated by a single CRLF are not split."""
        self.assert_result('foo bar\r\nspam eggs', ['foo bar spam eggs'])

    def test_two_LF(self):
        """Confirm lines separated by two newlines are split."""
        self.assert_result('foo bar\n\nspam eggs', ['foo bar', 'spam eggs'])

    def test_two_CRLF(self):
        """Confirm lines separated by two CRLF are split."""
        self.assert_result('foo bar\r\n\r\nspam eggs', ['foo bar', 'spam eggs'])

    def test_multiple_LF(self):
        """Confirm lines separated by more than two newlines are split."""
        self.assert_result('foo bar\n\n\nspam eggs', ['foo bar', 'spam eggs'])

    def test_multiple_CRLF(self):
        """Confirm lines separated by more than two CRLFs are split."""
        self.assert_result('foo bar\r\n\r\n\r\nspam eggs',
                           ['foo bar', 'spam eggs'])

    def test_leading_LF(self):
        """Confirm leading newlines do not create blank paragraphs."""
        self.assert_result('\n\nfoo bar', ['foo bar'])

    def test_leading_CRLF(self):
        """Confirm leading CRLFs do not create blank paragraphs."""
        self.assert_result('\r\n\r\nfoo bar', ['foo bar'])

    def test_trailing_LF(self):
        """Confirm trailing newlines do not create blank paragraphs."""
        self.assert_result('foo bar\n\n', ['foo bar'])

    def test_trailing_CRLF(self):
        """Confirm trailing CRLFs do not create blank paragraphs."""
        self.assert_result('foo bar\r\n\r\n', ['foo bar'])

    def test_whitespace_between_LF(self):
        """Confirm intervening whitespace between newlines is ignored."""
        self.assert_result('foo bar\n \t\nspam eggs',
                           ['foo bar', 'spam eggs'])

    def test_whitespace_between_CRLF(self):
        """Confirm intervening whitespace between CRLFs is ignored."""
        self.assert_result('foo bar\r\n \t\r\nspam eggs',
                           ['foo bar', 'spam eggs'])

    def assert_result(self, raw, expected):
        """Asserts a given string is split into expected paragraphs."""
        paras = atform.pdf.split_paragraphs(raw)
        self.assertEqual(expected, paras)


class BuildPath(unittest.TestCase):
    """Unit tests for the build_path() function."""

    def setUp(self):
        utils.reset()

    def test_no_section(self):
        """Confirm path created for a single-level ID."""
        self.assertEqual('root', atform.pdf.build_path((42,), 'root'))

    def test_single_section_no_title(self):
        """Confirm path created for an ID with one section and no title."""
        self.assertEqual(os.path.join('root', '42'),
                         atform.pdf.build_path((42, 1), 'root'))

    def test_single_section_title(self):
        """Confirm path created for an ID with one section with a title."""
        atform.id.section_titles[(42,)] = 'Spam'
        self.assertEqual(os.path.join('root', '42 Spam'),
                         atform.pdf.build_path((42, 1), 'root'))

    def test_multi_section_no_title(self):
        """Confirm path created for an ID with multiple sections with titles."""
        self.assertEqual(os.path.join('root', '42', '99'),
                         atform.pdf.build_path((42, 99, 1), 'root'))

    def test_multi_section_some_titles(self):
        """Confirm path created for an ID with multiple sections, some with titles."""
        atform.id.section_titles[(42, 99)] = 'Spam'
        self.assertEqual(os.path.join('root', '42', '99 Spam'),
                         atform.pdf.build_path((42, 99, 1), 'root'))

    def test_multi_section_all_titles(self):
        """Confirm path created for an ID with multiple sections, all with titles."""
        atform.id.section_titles[(42,)] = 'Foo'
        atform.id.section_titles[(42, 99)] = 'Bar'
        self.assertEqual(os.path.join('root', '42 Foo', '99 Bar'),
                         atform.pdf.build_path((42, 99, 1), 'root'))
