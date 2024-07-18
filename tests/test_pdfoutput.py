# This module contains PDF layout tests that cannot be validated
# programmatically with traditional assertion methods. These tests generate
# actual PDF files which must be visually verified.

from tests import utils
import testgen
import unittest


class PdfOutput(unittest.TestCase):

    def setUpClass():
        utils.reset()

        testgen.add_reference_category('References A', 'refa')
        testgen.add_reference_category('Some Other References B', 'refb')

        testgen.add_field('System (20 chars)', 20)
        testgen.add_field('Version (10 chars)', 10)

        testgen.add_signature('First Signature')
        testgen.add_signature('Second Signature')

    def tearDownClass():
        testgen.generate()

    def make_test(self, **kwargs):
        """testgen.Test() wrapper to assign a default title and objective."""
        title = self.id().split('.')[-1] # Remove module & class names.

        # Use the test's docstring as the default objective.
        kwargs.setdefault('objective', self.shortDescription())

        testgen.Test(title, **kwargs)

    def test_obj_single_paragraph(self):
        """Verify layout of an objective with a single paragraph."""
        self.make_test(objective="""
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        """
        )

    def test_obj_multi_paragraph(self):
        """Verify layout of an objective with multiple paragraphs."""
        self.make_test(objective="""
        This is the first paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

This is the second paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Duis at tellus at urna condimentum mattis pellentesque id. Aliquam nulla facilisi cras fermentum odio. Viverra ipsum nunc aliquet bibendum enim facilisis gravida neque convallis. Tempor orci eu lobortis elementum nibh tellus molestie nunc. Porttitor rhoncus dolor purus non enim praesent elementum facilisis leo.
        """
        )

    def test_ref_single(self):
        """Verify table layout with a single reference category."""
        self.make_test(
            references={'refa':['spam', 'eggs']}
        )

    def test_ref_multi(self):
        """Verify table layout with multiple reference categories."""
        self.make_test(
            references={
                'refa':['spam', 'eggs'],
                'refb':['foo', 'bar']
        })

    def test_equip_single(self):
        """Verify layout of a single required equipment."""
        self.make_test(
            equipment=['Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.']
        )

    def test_equip_multi(self):
        """Verify layout of multiple required equipment."""
        self.make_test(
            equipment=[
                'The first equipment.',
                'The second equipment.',
                'The last equipment.'
        ])


    def test_equip_multi_paragraph(self):
        """Verify layout of equipment items with multiple paragraphs."""
        self.make_test(
            equipment=[
                'The first equipment.',
                """The first paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eros in cursus turpis massa tincidunt dui ut ornare lectus. Fringilla urna porttitor rhoncus dolor purus. Enim blandit volutpat maecenas volutpat.

The second paragraph. Laoreet suspendisse interdum consectetur libero id faucibus nisl tincidunt. Donec et odio pellentesque diam. Posuere sollicitudin aliquam ultrices sagittis orci a scelerisque purus semper. Volutpat blandit aliquam etiam erat. Sed faucibus turpis in eu mi bibendum neque. At risus viverra adipiscing at. Amet consectetur adipiscing elit ut aliquam purus. Magna sit amet purus gravida.
                """,
                'The last equipment.'
            ])

    def test_precond_single(self):
        """Verify layout of a single precondition."""
        self.make_test(
            preconditions=['Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.']
        )

    def test_precond_multi(self):
        """Verify layout of multiple preconditions."""
        self.make_test(
            preconditions=[
                'The first precondition.',
                'The second precondition.',
                'The last precondition'
        ])

    def test_precond_multi_paragraphs(self):
        """Verify layout of precondition items with multiple paragraphs."""
        self.make_test(
            preconditions=[
                'The first precondition.',
                """The first paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Eros in cursus turpis massa tincidunt dui ut ornare lectus. Fringilla urna porttitor rhoncus dolor purus. Enim blandit volutpat maecenas volutpat.

The second paragraph. Laoreet suspendisse interdum consectetur libero id faucibus nisl tincidunt. Donec et odio pellentesque diam. Posuere sollicitudin aliquam ultrices sagittis orci a scelerisque purus semper. Volutpat blandit aliquam etiam erat. Sed faucibus turpis in eu mi bibendum neque. At risus viverra adipiscing at. Amet consectetur adipiscing elit ut aliquam purus. Magna sit amet purus gravida.
                """,
                'The last precondition'
            ])

    def test_proc_split(self):
        """Verify layout with a procedure list spanning multiple pages."""
        self.make_test(
            procedure=['Another procedure step'] * 40
        )

    def test_procedure_steps(self):
        """Verify layout of various procedure steps."""
        self.make_test(
            procedure=[
                """
                This is a procedure step with a single paragraph created
                as a simple string. Lorem ipsum dolor sit amet,
                consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Viverra
                aliquet eget sit amet tellus. Pharetra vel turpis nunc eget
                lorem dolor sed viverra ipsum. Libero justo laoreet sit
                amet cursus sit amet dictum sit. In dictum non consectetur a.
                """,

                """
                This is a procedure step with multiple paragraphs created
                as a simple string. Lorem ipsum dolor sit amet,
                consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Viverra
                aliquet eget sit amet tellus. Pharetra vel turpis nunc eget
                lorem dolor sed viverra ipsum. Libero justo laoreet sit
                amet cursus sit amet dictum sit. In dictum non consectetur a.

                This is the second paragraph. Dolor sit amet consectetur
                adipiscing elit pellentesque habitant. Vel fringilla est
                ullamcorper eget nulla facilisi etiam dignissim diam.
                Vitae proin sagittis nisl rhoncus mattis rhoncus. Nulla
                at volutpat diam ut venenatis tellus. Nisi porta lorem
                mollis aliquam.
                """,

                {
                    'text':"""
                    This is a procedure step with a single paragraph created
                    as a dictionary. Lorem ipsum dolor sit amet,
                    consectetur adipiscing elit, sed do eiusmod tempor
                    incididunt ut labore et dolore magna aliqua. Viverra
                    aliquet eget sit amet tellus.
                    """
                },

                {
                    'text':"""
                    This is a procedure step with multiple paragraphs created
                    as a dictionary. Lorem ipsum dolor sit amet,
                    consectetur adipiscing elit, sed do eiusmod tempor
                    incididunt ut labore et dolore magna aliqua. Viverra
                    aliquet eget sit amet tellus.

                    This is the second paragraph. Dolor sit amet consectetur
                    adipiscing elit pellentesque habitant. Vel fringilla est
                    ullamcorper eget nulla facilisi etiam dignissim diam.
                    Vitae proin sagittis nisl rhoncus mattis rhoncus.
                    Nulla at volutpat diam ut venenatis tellus. Nisi porta
                    lorem mollis aliquam.
                    """
                },

                {
                    'text':"""
                    This is a procedure step with a single data entry field
                    with no suffix.
                    """,
                    'fields':[
                        ('A Field', 10),
                    ]
                },

                {
                    'text':"""
                    This is a procedure step with multiple data entry fields,
                    all with suffixes.
                    """,
                    'fields':[
                        ('Spam', 10, 'Eggs'),
                        ('Foo', 3, 'Bar'),
                    ]
                },
            ])

    def test_page_count_single(self):
        """Verify correct footer page count for a single-page document."""
        self.make_test()

    def test_page_count_multi(self):
        """Verify correct footer page count for a multi-page document."""
        self.make_test(
            procedure=['Lots of steps'] * 60
        )

    def test_project_name(self):
        """Verify header project information with only a project name in the header."""
        testgen.misc.project_info = {'project':'The Project Name'}
        self.make_test()

    def test_system_name(self):
        """Verify header project information with only a system name in the header."""
        testgen.misc.project_info = {'system':'The System Name'}
        self.make_test()

    def test_project_system_name(self):
        """Verify header project information with project and system names in the header."""
        testgen.misc.project_info = {
            'project':'The Project Name',
            'system':'The System Name',
        }
        self.make_test()

    def test_text_formats(self):
        """Verify text formatting appearance."""
        # List of lines for all format combinations.
        cases = [
            'Leading text. '
            + testgen.format_text("This is {0} {1}.".format(typeface, font),
                                  typeface, font)
            + ' Trailing text. X'
            + testgen.format_text('X', typeface, font)
            for typeface, font in testgen.format.FONTS.keys()]

        self.make_test(
            objective="""
            Verify appearance of special text formats in the Objective,
            Equipment, Preconditions, and Procedure areas. Each line contains
            normal text surrounding the formatted text, with a pair of
            adjacent 'X' characters, one formatted and one normal, to verify
            relative vertical height.
            \n
            """
            + '\n\n'.join(cases),

            preconditions=cases,
            equipment=cases,
            procedure=cases,
        )
