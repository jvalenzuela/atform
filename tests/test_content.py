# Unit tests for the content module.


from tests import utils
import string
import testgen
import unittest


class Title(unittest.TestCase):
    """Unit tests for test titles."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string title."""
        with self.assertRaises(TypeError):
            testgen.Test(99)

    def test_empty(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(ValueError):
            testgen.Test('')

    def test_blank(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.Test(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = testgen.Test(string.whitespace + 'Spam' + string.whitespace)
        self.assertEqual('Spam', t.title)


class Objective(unittest.TestCase):
    """Unit tests for test objectives."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string objective."""
        with self.assertRaises(TypeError):
            testgen.Test('title', objective=42)

    def test_empty(self):
        """Confirm exception for an empty objective."""
        with self.assertRaises(ValueError):
            testgen.Test('title', objective='')

    def test_blank(self):
        """Confirm exception for an objective containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.Test('title', objective=string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = testgen.Test('title',
                         objective=string.whitespace + 'Spam' + string.whitespace)
        self.assertEqual('Spam', t.objective)


class References(unittest.TestCase):
    """Unit tests for test references."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-dict preconditions."""
        with self.assertRaises(TypeError):
            testgen.Test('title', references=[])

    def test_label_type(self):
        """Confirm exception for non-string labels."""
        with self.assertRaises(TypeError):
            testgen.Test('title', references={42: ['a']})

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(ValueError):
            testgen.Test('title', references={'': ['a']})

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.Test('title', references={string.whitespace: ['a']})

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from labels."""
        testgen.add_reference_category('refs', 'refs')
        t = testgen.Test('title', references={
            string.whitespace + 'refs' + string.whitespace: ['a']})
        self.assertIn('refs', t.references)

    def test_undefined_label(self):
        """Confirm exception for an unknown label."""
        with self.assertRaises(ValueError):
            testgen.Test('title', references={'foo': ['a']})

    def test_ref_type(self):
        """Confirm exception for a non-string reference."""
        testgen.add_reference_category('refs', 'refs')
        with self.assertRaises(TypeError):
            testgen.Test('title', references={'refs': [42]})

    def test_duplicate_ref(self):
        """Confirm exception for duplicate references."""
        testgen.add_reference_category('refs', 'refs')
        with self.assertRaises(ValueError):
            testgen.Test('title', references={'refs': ['a', 'a']})

    def test_ignore_empty_ref(self):
        """Confirm empty references are ignored."""
        testgen.add_reference_category('refs', 'refs')
        t = testgen.Test('title', references={'refs': ['a', '', '']})
        self.assertEqual(['a'], t.references['refs'])

    def test_ignore_blank_ref(self):
        """Confirm references containing only whitespace are ignored."""
        testgen.add_reference_category('refs', 'refs')
        t = testgen.Test('title', references={
            'refs': [string.whitespace, 'spam', string.whitespace]})
        self.assertEqual(['spam'], t.references['refs'])

    def test_strip_ref(self):
        """Confirm surrounding whitespace is removed from references."""
        testgen.add_reference_category('refs', 'refs')
        t = testgen.Test('title', references={
            'refs': [string.whitespace + 'foo' + string.whitespace]})
        self.assertEqual(['foo'], t.references['refs'])

    def test_ref_order(self):
        """Confirm references are stored in original order."""
        testgen.add_reference_category('refs', 'refs')
        t = testgen.Test('title', references={
            'refs': ['a', 'b', 'c']})
        self.assertEqual(['a', 'b', 'c'], t.references['refs'])

    def test_multiple_categories(self):
        """Confirm storage of multiple reference categories."""
        testgen.add_reference_category('Numbers', 'num')
        testgen.add_reference_category('Letters', 'alpha')
        t = testgen.Test('title', references={
            'num': ['1', '2', '3'],
            'alpha': ['a', 'b', 'c']})
        self.assertEqual(['1', '2', '3'], t.references['num'])
        self.assertEqual(['a', 'b', 'c'], t.references['alpha'])


class Preconditions(unittest.TestCase):
    """Unit tests for test preconditions."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-list preconditions."""
        with self.assertRaises(TypeError):
            testgen.Test('title', preconditions='spam')

    def test_item_type(self):
        """Confirm exception for a non-string list item."""
        with self.assertRaises(TypeError):
            testgen.Test('title', preconditions=[42])

    def test_empty(self):
        """Confirm exception for an empty item."""
        with self.assertRaises(ValueError):
            testgen.Test('title', preconditions=[''])

    def test_blank(self):
        """Confirm exception for an item containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.Test('title', preconditions=[string.whitespace])

    def test_strip(self):
        """Confirm surrounding whitespace is removed from list items."""
        t = testgen.Test('title',
                         preconditions=[string.whitespace
                                        + 'Foo'
                                        + string.whitespace])
        self.assertEqual('Foo', t.preconditions[0])


class Procedure(unittest.TestCase):
    """Unit tests for the procedure parameter."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-list procedure."""
        with self.assertRaises(TypeError):
            testgen.Test('title', procedure='spam')

    def test_item_type(self):
        """Confirm exception for a non-string list item."""
        with self.assertRaises(TypeError):
            testgen.Test('title', procedure=[42])

    def test_empty(self):
        """Confirm exception for an empty item."""
        with self.assertRaises(ValueError):
            testgen.Test('title', procedure=[''])

    def test_blank(self):
        """Confirm exception for an item containing only whitespace."""
        with self.assertRaises(ValueError):
            testgen.Test('title', procedure=[string.whitespace])

    def test_strip(self):
        """Confirm surrounding whitespace is removed from list items."""
        t = testgen.Test('title',
                         procedure=[string.whitespace
                                    + 'Foo'
                                    + string.whitespace])
        self.assertEqual('Foo', t.procedure[0])


class Generate(unittest.TestCase):
    """Unit tests for the generate() function."""

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(TypeError):
            testgen.generate(42)
