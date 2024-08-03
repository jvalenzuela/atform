# Unit tests for the content module.


from tests import utils
import string
import atform
import unittest


class Title(unittest.TestCase):
    """Unit tests for test titles."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string title."""
        with self.assertRaises(SystemExit):
            atform.Test(99)

    def test_empty(self):
        """Confirm exception for an empty title."""
        with self.assertRaises(SystemExit):
            atform.Test('')

    def test_blank(self):
        """Confirm exception for a title containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = atform.Test(string.whitespace + 'Spam' + string.whitespace)
        self.assertEqual('Spam', t.title)


class Label(unittest.TestCase):
    """Unit tests for label replacement."""

    def setUp(self):
        utils.reset()

    def test_objective_placeholder(self):
        """Confirm placeholders are replaced in the objective."""
        atform.Test('target', label='TheLabel')
        t = atform.Test('title', objective='$TheLabel')
        t._pregenerate()
        self.assertEqual('1', t.objective)

    def test_precondition_placeholder(self):
        """Confirm placeholders are replaced in preconditions."""
        atform.Test('target', label='TheLabel')
        t = atform.Test('title', preconditions=['$TheLabel'])
        t._pregenerate()
        self.assertEqual('1', t.preconditions[0])

    def test_procedure_step_string_placeholder(self):
        """Confirm placeholders are replaced in string procedure steps."""
        atform.Test('target', label='TheLabel')
        t = atform.Test('title', procedure=['$TheLabel'])
        t._pregenerate()
        self.assertEqual('1', t.procedure[0].text)

    def test_procedure_step_dict_placeholder(self):
        """Confirm placeholders are replaced in dict procedure steps."""
        atform.Test('target', label='TheLabel')
        t = atform.Test('title', procedure=[{'text':'$TheLabel'}])
        t._pregenerate()
        self.assertEqual('1', t.procedure[0].text)

    def test_forward_reference(self):
        """Confirm a placeholder for a label defined in a later test."""
        t = atform.Test('title', objective='$TheLabel')
        atform.Test('target', label='TheLabel')
        t._pregenerate()
        self.assertEqual('2', t.objective)


class Objective(unittest.TestCase):
    """Unit tests for test objectives."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-string objective."""
        with self.assertRaises(SystemExit):
            atform.Test('title', objective=42)

    def test_empty(self):
        """Confirm exception for an empty objective."""
        with self.assertRaises(SystemExit):
            atform.Test('title', objective='')

    def test_blank(self):
        """Confirm exception for an objective containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test('title', objective=string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        t = atform.Test('title',
                        objective=string.whitespace + 'Spam' + string.whitespace)
        self.assertEqual('Spam', t.objective)


class References(unittest.TestCase):
    """Unit tests for test references."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for non-dict preconditions."""
        with self.assertRaises(SystemExit):
            atform.Test('title', references=[])

    def test_label_type(self):
        """Confirm exception for non-string labels."""
        with self.assertRaises(SystemExit):
            atform.Test('title', references={42: ['a']})

    def test_empty_label(self):
        """Confirm exception for an empty label."""
        with self.assertRaises(SystemExit):
            atform.Test('title', references={'': ['a']})

    def test_blank_label(self):
        """Confirm exception for a label containing only whitespace."""
        with self.assertRaises(SystemExit):
            atform.Test('title', references={string.whitespace: ['a']})

    def test_label_strip(self):
        """Confirm surrounding whitespace is removed from labels."""
        atform.add_reference_category('refs', 'refs')
        t = atform.Test('title', references={
            string.whitespace + 'refs' + string.whitespace: ['a']})
        self.assertIn('refs', t.references)

    def test_undefined_label(self):
        """Confirm exception for an unknown label."""
        with self.assertRaises(SystemExit):
            atform.Test('title', references={'foo': ['a']})

    def test_ref_type(self):
        """Confirm exception for a non-list reference value."""
        atform.add_reference_category('refs', 'refs')
        with self.assertRaises(TypeError):
            atform.Test('title', references={'refs': 'spam'})

    def test_ref_item_type(self):
        """Confirm exception for a non-string reference items."""
        atform.add_reference_category('refs', 'refs')
        with self.assertRaises(SystemExit):
            atform.Test('title', references={'refs': [42]})

    def test_duplicate_ref(self):
        """Confirm exception for duplicate references."""
        atform.add_reference_category('refs', 'refs')
        with self.assertRaises(SystemExit):
            atform.Test('title', references={'refs': ['a', 'a']})

    def test_ignore_empty_ref(self):
        """Confirm empty references are ignored."""
        atform.add_reference_category('refs', 'refs')
        t = atform.Test('title', references={'refs': ['a', '', '']})
        self.assertEqual(['a'], t.references['refs'])

    def test_ignore_blank_ref(self):
        """Confirm references containing only whitespace are ignored."""
        atform.add_reference_category('refs', 'refs')
        t = atform.Test('title', references={
            'refs': [string.whitespace, 'spam', string.whitespace]})
        self.assertEqual(['spam'], t.references['refs'])

    def test_strip_ref(self):
        """Confirm surrounding whitespace is removed from references."""
        atform.add_reference_category('refs', 'refs')
        t = atform.Test('title', references={
            'refs': [string.whitespace + 'foo' + string.whitespace]})
        self.assertEqual(['foo'], t.references['refs'])

    def test_ref_order(self):
        """Confirm references are stored in original order."""
        atform.add_reference_category('refs', 'refs')
        t = atform.Test('title', references={
            'refs': ['a', 'b', 'c']})
        self.assertEqual(['a', 'b', 'c'], t.references['refs'])

    def test_multiple_categories(self):
        """Confirm storage of multiple reference categories."""
        atform.add_reference_category('Numbers', 'num')
        atform.add_reference_category('Letters', 'alpha')
        t = atform.Test('title', references={
            'num': ['1', '2', '3'],
            'alpha': ['a', 'b', 'c']})
        self.assertEqual(['1', '2', '3'], t.references['num'])
        self.assertEqual(['a', 'b', 'c'], t.references['alpha'])


class StringList(object):
    """Base class for testing a parameter that accepts a list of strings."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-list.."""
        with self.assertRaises(SystemExit):
            self.call('spam')

    def test_item_type(self):
        """Confirm exception for a non-string list item."""
        with self.assertRaises(SystemExit):
            self.call([42])

    def test_empty(self):
        """Confirm exception for an empty item."""
        with self.assertRaises(SystemExit):
            self.call([''])

    def test_blank(self):
        """Confirm exception for an item containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.call([string.whitespace])

    def test_strip(self):
        """Confirm surrounding whitespace is removed from list items."""
        t = self.call([string.whitespace + 'Foo' + string.whitespace])
        self.assertEqual('Foo', getattr(t, self.parameter_name)[0])

    def call(self, value):
        """Calls Test() with a given parameter value."""
        args = {self.parameter_name: value}
        return atform.Test('title', **args)


class Equipment(StringList, unittest.TestCase):
    """Unit tests for test equipment."""
    parameter_name = 'equipment'


class Preconditions(StringList, unittest.TestCase):
    """Unit tests for test preconditions."""
    parameter_name = 'preconditions'


class ProcedureList(unittest.TestCase):
    """Unit tests for the procedure list."""

    def setUp(self):
        utils.reset()

    def test_type(self):
        """Confirm exception for a non-list.."""
        with self.assertRaises(SystemExit):
            atform.Test('test', procedure='spam')


class ProcedureStepBase(object):
    """Base class for procedure step tests."""

    def setUp(self):
        utils.reset()

    def make_step(self, step):
        """Creates a test with a given procedure step."""
        return atform.Test('test', procedure=[step])

    def make_field(self, field):
        """Creates a test with a given procedure step field."""
        return self.make_step({
            'text':'text',
            'fields':[field],
        })


class ProcedureStepString(ProcedureStepBase, unittest.TestCase):
    """Unit tests for string procedure steps."""

    def test_type(self):
        """Confirm exception for a non-string."""
        with self.assertRaises(SystemExit):
            self.make_step(42)

    def test_empty(self):
        """Confirm exception for an empty string."""
        with self.assertRaises(SystemExit):
            self.make_step('')

    def test_blank(self):
        """Confirm exception for a string containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_step(string.whitespace)

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the string."""
        t = self.make_step(string.whitespace + 'Foo' + string.whitespace)
        self.assertEqual('Foo', t.procedure[0].text)


class ProcedureStepDict(ProcedureStepBase, unittest.TestCase):
    """Unit tests for dictionary procedure steps."""

    def test_unknown_key(self):
        """Confirm exception for an undefined key."""
        with self.assertRaises(SystemExit):
            self.make_step({'text':'spam', 'foo':'bar'})


class ProcedureStepDictText(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step dict text key."""

    def test_missing(self):
        """Confirm exception if text key is missing."""
        with self.assertRaises(SystemExit):
            self.make_step({})

    def test_type(self):
        """Confirm exception if text is not a string."""
        with self.assertRaises(SystemExit):
            self.make_step({'text':99})

    def test_empty(self):
        """Confirm exception if text is empty."""
        with self.assertRaises(SystemExit):
            self.make_step({'text':''})

    def test_blank(self):
        """Confirm exception if text contains only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_step({'text':string.whitespace})

    def test_strip(self):
        """Confirm surrounding whitespace is removed."""
        test = self.make_step({
            'text':string.whitespace + 'foo' + string.whitespace
        })
        self.assertEqual('foo', test.procedure[0].text)


class ProcedureStepFields(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field definitions."""

    def test_type(self):
        """Confirm exception for a non-list fields key."""
        with self.assertRaises(SystemExit):
            self.make_step({'text':'text', 'fields':'not a list'})

    def test_item_type(self):
        """Confirm exception for a non-tuple list item."""
        with self.assertRaises(SystemExit):
            self.make_field('not a tuple')

    def test_empty_item(self):
        """Confirm exception for an empty field tuple."""
        with self.assertRaises(SystemExit):
            self.make_field(())

    def test_too_long(self):
        """Confirm exception for a field definition with too many items."""
        with self.assertRaises(SystemExit):
            self.make_field(('field', 1, 'suffix', 42))


class ProcedureStepFieldTitle(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field title."""

    def test_type(self):
        """Confirm exception for a non-string field title."""
        with self.assertRaises(SystemExit):
            self.make_field((None, 1))

    def test_empty(self):
        """Confirm exception for an empty field title."""
        with self.assertRaises(SystemExit):
            self.make_field(('', 1))

    def test_blank(self):
        """Confirm exception for a field title containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_field((string.whitespace, 1))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from field titles."""
        t = self.make_field((string.whitespace + 'foo' + string.whitespace, 1))
        self.assertEqual('foo', t.procedure[0].fields[0].title)


class ProcedureStepFieldLength(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field length."""

    def test_type(self):
        """Confirm exception for a non-integer length."""
        with self.assertRaises(SystemExit):
            self.make_field(('field', '42'))

    def test_missing(self):
        """Confirm exception for a missing length."""
        with self.assertRaises(SystemExit):
            self.make_field(('field',))

    def test_invalid_length(self):
        """Confirm exception for a length less than one."""
        for i in [-1, 0]:
            with self.assertRaises(SystemExit):
                self.make_field(('field', i))


class ProcedureStepFieldSuffix(ProcedureStepBase, unittest.TestCase):
    """Unit tests for procedure step field suffix."""

    def test_type(self):
        """Confirm exception for a non-string suffix."""
        with self.assertRaises(SystemExit):
            self.make_field(('field', 1, 42))

    def test_empty(self):
        """Confirm exception for an empty suffix."""
        with self.assertRaises(SystemExit):
            self.make_field(('field', 1, ''))

    def test_blank(self):
        """Confirm exception for a suffix containing only whitespace."""
        with self.assertRaises(SystemExit):
            self.make_field(('field', 1, string.whitespace))

    def test_strip(self):
        """Confirm surrounding whitespace is removed from the suffix."""
        t = self.make_field(
            ('field', 1, string.whitespace + 'foo' + string.whitespace))
        self.assertEqual('foo', t.procedure[0].fields[0].suffix)


class TestProjectInfo(unittest.TestCase):
    """Unit tests for project information stored in a Test() instance."""

    def setUp(self):
        utils.reset()

    def test_capture(self):
        """Confirm accurate information is captured when instantiated."""
        info = {'project':'foo', 'system':'spam'}
        atform.set_project_info(**info)
        t = atform.Test('A test')
        self.assertEqual(info, t.project_info)

    def test_update_between_tests(self):
        """Confirm system information changes do not affect existing tests."""
        atform.set_project_info(project='foo', system='bar')
        t1 = atform.Test('Test 1')

        atform.set_project_info(project='spam', system='eggs')
        t2 = atform.Test('Test 2')

        self.assertEqual({'project':'foo', 'system':'bar'}, t1.project_info)
        self.assertEqual({'project':'spam', 'system':'eggs'}, t2.project_info)


class Generate(unittest.TestCase):
    """Unit tests for the generate() function."""

    def test_path_type(self):
        """Confirm exception if path is not a string."""
        with self.assertRaises(SystemExit):
            atform.generate(42)
