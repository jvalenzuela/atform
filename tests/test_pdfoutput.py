# This module contains PDF layout tests that cannot be validated
# programmatically with traditional assertion methods. These tests generate
# actual PDF files which must be visually verified.

from tests import utils
import testgen
import string
import unittest
from unittest.mock import patch


class Base(object):
    """Base class for tests which generate PDFs."""

    def setUp(self):
        utils.reset()

    def make_test(self, generate=True, **kwargs):
        """testgen.Test() wrapper to assign a title and default objective."""
        # Generate a title that is class_name.method_name.
        title = '.'.join(self.id().split('.')[-2:])

        # Use the test's docstring as the default objective.
        kwargs.setdefault('objective', self.shortDescription())

        testgen.Test(title, **kwargs)
        if generate:
            testgen.generate()


class VersionControl(Base, unittest.TestCase):
    """Generate PDFs under various version control conditions."""

    @patch('testgen.vcs.Git')
    def test_no_version_control(self, mock):
        """Verify no draft mark or version in footer."""
        mock.side_effect = testgen.vcs.NoVersionControlError
        self.make_test()

    @patch.object(testgen.vcs.Git, 'clean', new=False)
    @patch.object(testgen.vcs.Git, 'version', new='foo')
    def test_draft(self):
        """Verify draft mark and no version in the footer."""
        self.make_test()

    @patch.object(testgen.vcs.Git, 'clean', new=True)
    @patch.object(testgen.vcs.Git, 'version', new='spam')
    def test_clean(self):
        """Verify version in the footer and no draft mark."""
        self.make_test()


class Objective(Base, unittest.TestCase):
    """Tests for the Objective section."""

    def test_single_paragraph(self):
        """Verify layout of a single paragraph."""
        self.make_test(objective="""
        Verify layout of a single paragraph.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat
        nulla pariatur.
        """)

    def test_multi_paragraph(self):
        """Verify layout of multiple paragraphs."""
        self.make_test(objective="""
        This is the first paragraph. Lorem ipsum dolor sit amet, consectetur
        adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
        ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
        irure dolor in reprehenderit in voluptate velit esse cillum dolore
        eu fugiat nulla pariatur.

        This is the second paragraph. Lorem ipsum dolor sit amet, consectetur
        adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        magna aliqua. Duis at tellus at urna condimentum mattis pellentesque
        id. Aliquam nulla facilisi cras fermentum odio. Viverra ipsum nunc
        aliquet bibendum enim facilisis gravida neque convallis. Tempor orci
        eu lobortis elementum nibh tellus molestie nunc. Porttitor rhoncus
        dolor purus non enim praesent elementum facilisis leo.
        """)


class References(Base, unittest.TestCase):
    """Tests for the References section."""

    def test_single(self):
        """Verify table layout with a single reference category."""
        testgen.add_reference_category('Single Reference', 'single')
        self.make_test(
            references={'single':['spam']}
        )

    def test_multiple(self):
        """Verify table layout with multiple reference categories."""
        testgen.add_reference_category('Single Reference', 'single')
        testgen.add_reference_category('Multiple References', 'multi')
        testgen.add_reference_category('Long List', 'long')
        self.make_test(
            references={
                'single':['spam'],
                'multi':['foo', 'bar'],

                # Long enough to require breaking across multiple lines.
                'long':[str(x) for x in range(50)],
        })


class Equipment(Base, unittest.TestCase):
    """Tests for the Equipment section."""

    def test_single(self):
        """Verify layout of a single equipment item."""
        self.make_test(
            equipment=[
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore
                magna aliqua."""
            ])

    def test_multiple(self):
        """Verify layout of multiple equipment items."""
        self.make_test(
            equipment=[
                'The first equipment.',
                """The second equipment with multiple paragraphs.
                Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore magna
                aliqua. Eros in cursus turpis massa tincidunt dui ut ornare
                lectus. Fringilla urna porttitor rhoncus dolor purus.
                Enim blandit volutpat maecenas volutpat.

                The second paragraph. Laoreet suspendisse interdum consectetur
                libero id faucibus nisl tincidunt. Donec et odio pellentesque
                diam. Posuere sollicitudin aliquam ultrices sagittis orci a
                scelerisque purus semper. Volutpat blandit aliquam etiam erat.
                Sed faucibus turpis in eu mi bibendum neque. At risus viverra
                adipiscing at. Amet consectetur adipiscing elit ut aliquam
                purus. Magna sit amet purus gravida.
                """,
                'The last equipment.'
            ])


class Fields(Base, unittest.TestCase):
    """Tests for Environment section fields."""

    def test_single(self):
        """Verify layout of a single field."""
        testgen.add_field('Only Field (10 chars)', 10)
        self.make_test()

    def test_multiple(self):
        testgen.add_field('First Field (5 chars)', 5)
        testgen.add_field('Second Field (10 chars)', 10)
        self.make_test()


class Preconditions(Base, unittest.TestCase):
    """Tests for the Preconditions section."""

    def test_single(self):
        """Verify layout of a single item."""
        self.make_test(preconditions=[
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
            sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua."""
        ])

    def test_multiple(self):
        """Verify layout of multiple items."""
        self.make_test(preconditions=[
            'The first precondition.',
            """The second precondition with multiple paragraphs. Lorem ipsum
            dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Eros in
            cursus turpis massa tincidunt dui ut ornare lectus. Fringilla
            urna porttitor rhoncus dolor purus. Enim blandit volutpat
            maecenas volutpat.

            The second paragraph. Laoreet suspendisse interdum consectetur
            libero id faucibus nisl tincidunt. Donec et odio pellentesque diam.
            Posuere sollicitudin aliquam ultrices sagittis orci a scelerisque
            purus semper. Volutpat blandit aliquam etiam erat. Sed faucibus
            turpis in eu mi bibendum neque. At risus viverra adipiscing at.
            Amet consectetur adipiscing elit ut aliquam purus. Magna sit amet
            purus gravida.
            """,
            'The last precondition.'
        ])


class Procedure(Base, unittest.TestCase):
    """Tests for the Procedure section."""

    def test_steps(self):
        """Verify procedure step table layout."""
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
        ]

        # Add enough steps to force the table to span muliple pages.
        [procedure.append('Dummy step') for i in range(10)]

        self.make_test(procedure=procedure)


class Approval(Base, unittest.TestCase):
    """Tests for the Approval section."""

    def test_single(self):
        """Verify layout with a single signature entry and date tooltip."""
        testgen.add_signature('Only Signature')
        self.make_test()

    def test_multiple(self):
        """Verify layout with multiple signature entries."""
        testgen.add_signature('First Signature')
        testgen.add_signature('Second Signature')
        testgen.add_signature('Third Signature')
        self.make_test()


class ProjectInfo(Base, unittest.TestCase):
    """Tests for header project information."""

    def test_project(self):
        """Verify only project name in the header."""
        testgen.set_project_info(project='The Project Name')
        self.make_test()

    def test_system(self):
        """Verify only system name in the header."""
        testgen.set_project_info(system='The System Name')
        self.make_test()

    def test_project_and_system(self):
        """Verify project and system names in the header."""
        testgen.set_project_info(
            project='The Project Name',
            system='The System Name',
        )
        self.make_test()


class Format(Base, unittest.TestCase):
    """Tests for text formatting."""

    def test_formats(self):
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
            Verify appearance of special text formats. Each line contains
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

    def test_bullet_list(self):
        """Verify bullet list appearance."""
        single = "This is a single-item list:" + testgen.bullet_list(
            'The only item.')
        multi = "A multi-item list with formatted items:" + testgen.bullet_list(
            'First item',

            'An ' + testgen.format_text('italic', font='italic') + ' item',

            string.whitespace
            + 'Item surrounded by whitespace.'
            + string.whitespace,

            'Last item')

        self.make_test(
            objective="Verify appearance of bullet lists in various contexts."
            + single + multi,

            equipment=[single, multi],
            preconditions=[single, multi],
            procedure=[single, multi],
        )


class PageCount(Base, unittest.TestCase):
    """Tests for the page count in the footer."""

    def test_page_count_single(self):
        """Verify correct footer page count for a single-page document."""
        self.make_test()

    def test_page_count_multi(self):
        """Verify correct footer page count for a multi-page document."""
        self.make_test(procedure=['Lots of steps'] * 60)
