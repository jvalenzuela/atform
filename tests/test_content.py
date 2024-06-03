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
