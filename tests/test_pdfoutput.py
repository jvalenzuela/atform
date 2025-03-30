# This module contains PDF layout tests that cannot be validated
# programmatically with traditional assertion methods. These tests generate
# actual PDF files which must be visually verified.

from tests import utils
import atform
import functools
import os
import string
import unittest
from unittest.mock import patch


class Base(object):
    """Base class for tests which generate PDFs."""

    def setUp(self):
        utils.reset()

    @utils.disable_idlock
    @utils.no_args
    def make_test(self, generate=True, **kwargs):
        """atform.add_test() wrapper to assign a title and default objective."""
        # Generate a title that is class_name.method_name.
        title = ".".join(self.id().split(".")[-2:])

        # Use the test's docstring as the default objective.
        kwargs.setdefault("objective", self.shortDescription())

        atform.add_test(title, **kwargs)
        if generate:
            atform.generate()


def nosplit(method):
    """Decorator for methods verifying a section is not split across pages.

    This works by patching the distance between sections to create a large
    amount of space after the Objective section, forcing the section
    being tested to the bottom of the first page. The wrapped test method
    then only needs to make the section being tested suitably long enough
    that it would be split across the page break.
    """

    @patch.object(atform.pdf.layout, "SECTION_SEP", new=530)
    @functools.wraps(method)
    def wrapper(self):
        method(self)

    return wrapper


class VersionControl(Base, unittest.TestCase):
    """Generate PDFs under various version control conditions."""

    @patch("atform.vcs.Git")
    def test_no_version_control(self, mock):
        """Verify no draft mark or version in footer."""
        mock.side_effect = atform.vcs.NoVersionControlError
        self.make_test()

    @patch.object(atform.vcs.Git, "clean", new=False)
    @patch.object(atform.vcs.Git, "version", new="foo")
    def test_draft(self):
        """Verify draft mark and no version in the footer."""
        self.make_test()

    @patch.object(atform.vcs.Git, "clean", new=True)
    @patch.object(atform.vcs.Git, "version", new="spam")
    def test_clean(self):
        """Verify version in the footer and no draft mark."""
        self.make_test()


class Objective(Base, unittest.TestCase):
    """Tests for the Objective section."""

    def test_single_paragraph(self):
        """Verify layout of a single paragraph."""
        self.make_test(
            objective="""
        Verify layout of a single paragraph.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
        reprehenderit in voluptate velit esse cillum dolore eu fugiat
        nulla pariatur.
        """
        )

    def test_multi_paragraph(self):
        """Verify layout of multiple paragraphs."""
        self.make_test(
            objective="""
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
        """
        )


class References(Base, unittest.TestCase):
    """Tests for the References section."""

    def test_single(self):
        """Verify table layout with a single reference category."""
        atform.add_reference_category("Single Reference", "single")
        self.make_test(references={"single": ["spam"]})

    def test_multiple(self):
        """Verify table layout with multiple reference categories."""
        atform.add_reference_category("Single Reference", "single")
        atform.add_reference_category("Multiple References", "multi")
        atform.add_reference_category("Long List", "long")
        self.make_test(
            references={
                "single": ["spam"],
                "multi": ["foo", "bar"],
                # Long enough to require breaking across multiple lines.
                "long": [str(x) for x in range(50)],
            }
        )

    @nosplit
    def test_nosplit(self):
        """Verify references section is on the top of the second page."""
        num_refs = 10
        [atform.add_reference_category(f"r{i}", f"r{i}") for i in range(num_refs)]

        self.make_test(references=dict([(f"r{i}", ["spam"]) for i in range(num_refs)]))


class Equipment(Base, unittest.TestCase):
    """Tests for the Equipment section."""

    def test_single(self):
        """Verify layout of a single equipment item."""
        self.make_test(
            equipment=[
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore
                magna aliqua."""
            ]
        )

    def test_multiple(self):
        """Verify layout of multiple equipment items."""
        self.make_test(
            equipment=[
                "The first equipment.",
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
                "The last equipment.",
            ]
        )

    @nosplit
    def test_nosplit(self):
        """Verify Equipment section is at the top of the second page."""
        self.make_test(equipment=[str(i) for i in range(10)])


class Fields(Base, unittest.TestCase):
    """Tests for Environment section fields."""

    def test_single(self):
        """Verify layout of a single field."""
        atform.add_field(
            "Enter 'Xy'; verify cap height and descender",
            3,
            "f",
        )
        self.make_test()

    def test_multiple(self):
        """Verify layout of multiple fields."""
        atform.add_field("Enter 'MM', verify width.", 2, "f1")
        atform.add_field("Second Field (10 chars)", 10, "f2")
        self.make_test()

    @nosplit
    def test_nosplit(self):
        """Verify Environment section starts at the top of the second page."""
        [atform.add_field(f"f{i}", 5, f"f{i}") for i in range(10)]
        self.make_test()


class Preconditions(Base, unittest.TestCase):
    """Tests for the Preconditions section."""

    def test_single(self):
        """Verify layout of a single item."""
        self.make_test(
            preconditions=[
                """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
            sed do eiusmod tempor incididunt ut labore et dolore
            magna aliqua."""
            ]
        )

    def test_multiple(self):
        """Verify layout of multiple items."""
        self.make_test(
            preconditions=[
                "The first precondition.",
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
                "The last precondition.",
            ]
        )

    @nosplit
    def test_nosplit(self):
        """Verify Preconditions starts at the top of the second page."""
        self.make_test(preconditions=[str(i) for i in range(10)])


class Procedure(Base, unittest.TestCase):
    """Tests for the Procedure section."""

    def test_steps(self):
        """Verify procedure step table layout."""
        procedure = [
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
                "text": """
                This is a procedure step with a single paragraph created
                as a dictionary. Lorem ipsum dolor sit amet,
                consectetur adipiscing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Viverra
                aliquet eget sit amet tellus.
                """
            },
            {
                "text": """
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
                "text": """
                This is a procedure step with a single data entry field
                with no suffix.
                """,
                "fields": [
                    ("A Field", 10),
                ],
            },
            {
                "text": """
                This is a procedure step with a single data entry field
                with a suffix.
                """,
                "fields": [
                    ("Spam Eggs", 10, "Foo Bar"),
                ],
            },
            {
                "text": """
                This is a procedure step with multiple data entry fields,
                all with suffixes. Ensure field titles are right-justified
                and suffixes are left-justified against the text entry
                field.
                """,
                "fields": [
                    ("Spam", 10, "Eggs"),
                    ("A Long Title", 3, "Bar"),
                ],
            },
            self.make_image_step("full"),
            self.make_image_step("width"),
            self.make_image_step("height"),
            self.make_image_step("small"),
            {
                # This step exists to verify correct operation with a PNG
                # image. Testing image size limits is not done with PNG
                # images; see test_image.ErrorBase.test_too_large for
                # rationale.
                "text": """
                Procedure step with a PNG image. Verify a circle inscribed
                by a square.
                """,
                "image": os.path.join("tests", "images", "procedure", "step.png"),
            },
        ]

        # Add enough steps to force the table to span muliple pages.
        [procedure.append("Dummy step") for i in range(10)]

        self.make_test(procedure=procedure)

    def make_image_step(self, size):
        """Creates a procedure step verifying an optional image."""
        return {
            "text": f"""
            Verify procedure step layout with image size: {size}

            Confirm image has a red border, the shape in the middle is a circle, and
            clearance from surrounding text and fields.

            jpqy Bottom text line with descenders.
            """,
            "image": os.path.join("tests", "images", "procedure", f"{size}.jpg"),
            "fields": [
                ("field", 1),
            ],
        }

    def test_dup_image(self):
        """Confirm the same image can be used in separate tests.

        The intent is to verify the same ReportLab Image flowable can be used
        multiple times.
        """
        step = {
            "text": "Step with image.",
            "image": os.path.join("tests", "images", "procedure", "small.jpg"),
        }
        self.make_test(
            objective="Confirm the same image appearing in multiple procedure steps.",
            procedure=[step] * 2,
        )
        self.make_test(
            objective="Confirm the same image used in multiple tests.",
            procedure=[step],
        )

    def test_nosplit_first_step(self):
        """Verify Procedure section starts at the top of the second page.

        This is a null test because there does seeem to be a way to get
        Reportlab to split the procedure table between the the header row
        and first step.
        """
        pass

    @nosplit
    def test_nosplit_last_row(self):
        """Verify the second page starts with the last step."""
        self.make_test(procedure=["step"] * 2)


class Notes(Base, unittest.TestCase):
    """Tests for the Notes section."""

    @nosplit
    def test_nosplit(self):
        """Verify the Notes section starts at the top of the second page."""
        self.make_test()


class Approval(Base, unittest.TestCase):
    """Tests for the Approval section."""

    def test_single(self):
        """Verify layout with a single signature entry and date tooltip."""
        atform.add_signature("Only Signature")
        self.make_test()

    def test_multiple(self):
        """Verify layout with multiple signature entries."""
        atform.add_signature("First Signature")
        atform.add_signature("Second Signature")
        atform.add_signature("Third Signature")
        self.make_test()

    def test_nosplit(self):
        """Verify approval section is on the top of the second page.

        This method does not use the @nosplit decorator because
        the Approval section comes after Notes, so it just creates
        enough signature entries to require a page break.
        """
        [atform.add_signature(f"Sig{i}") for i in range(25)]
        self.make_test()


class TitleBlock(Base, unittest.TestCase):
    """Tests for title block on the first page."""

    def test_none(self):
        """Verify header when no logo or project information is present."""
        procedure = [
            "Verify first page has the same header as the second page.",
        ]

        # Add dummy content to generate multiple pages.
        procedure.extend(["filler step"] * 50)

        self.make_test(procedure=procedure)

    def test_project(self):
        """Verify only project name in the title block."""
        atform.set_project_info(project="The Project Name")
        self.make_test()

    def test_system(self):
        """Verify only system name in the title block."""
        atform.set_project_info(system="The System Name")
        self.make_test()

    def test_logo_only(self):
        """Verify layout with only a logo."""
        atform.add_logo(os.path.join("tests", "images", "logo", "full.jpg"))
        self.make_test(
            procedure=[
                "Verify title is in the lower-right corner of the title block.",
            ],
        )

    def test_short_logo(self):
        """Verify layout with a logo shorter than the text fields."""
        atform.set_project_info(
            project="The Project Name",
            system="The System Name",
        )
        atform.add_logo(os.path.join("tests", "images", "logo", "width.jpg"))
        self.make_test(
            procedure=[
                "Verify logo is vertically centered with text fields.",
            ],
        )

    def test_tall_logo(self):
        """Verify layout with a logo taller than the text fields."""
        atform.set_project_info(
            project="The Project Name",
            system="The System Name",
        )
        atform.add_logo(os.path.join("tests", "images", "logo", "full.jpg"))
        self.make_test(
            procedure=[
                """
                Verify project and system names are together in the upper-right
                corner of the title block.
                """,
                "Verify title is in the lower-right corner of the title block.",
            ],
        )

    def test_project_and_system_a_very_long_name_to_generate_a_multiline_title(self):
        """Verify layout of a title block with multi-line text."""
        atform.add_logo(os.path.join("tests", "images", "logo", "full.jpg"))
        # Generate long project and system strings to ensure they require
        # multiple lines.
        atform.set_project_info(
            project="The Project Name " + "." * 100,
            system="The System Name " + "." * 100,
        )
        self.make_test(
            procedure=[
                "Verify horizontal padding between logo and title block text.",
            ],
        )


class Format(Base, unittest.TestCase):
    """Tests for text formatting."""

    def test_formats(self):
        """Verify text formatting appearance."""
        # List of lines for all format combinations.
        cases = [
            "Leading text. "
            + atform.format_text(
                "This is {0} {1}.".format(typeface, font),
                typeface=typeface,
                font=font,
            )
            + " Trailing text. X"
            + atform.format_text(
                "X",
                typeface=typeface,
                font=font,
            )
            for typeface, font in atform.format.FONTS.keys()
        ]

        self.make_test(
            objective="""
            Verify appearance of special text formats. Each line contains
            normal text surrounding the formatted text, with a pair of
            adjacent 'X' characters, one formatted and one normal, to verify
            relative vertical height.
            \n
            """
            + "\n\n".join(cases),
            preconditions=cases,
            equipment=cases,
            procedure=cases,
        )

    def test_bullet_list(self):
        """Verify bullet list appearance."""
        single = "This is a single-item list:" + atform.bullet_list("The only item.")
        multi = "A multi-item list with formatted items:" + atform.bullet_list(
            "First item",
            "An " + atform.format_text("italic", font="italic") + " item",
            string.whitespace + "Item surrounded by whitespace." + string.whitespace,
            "Last item",
        )

        self.make_test(
            objective="Verify appearance of bullet lists in various contexts."
            + single
            + multi,
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
        self.make_test(procedure=["Lots of steps"] * 60)


class Logo(Base, unittest.TestCase):
    """Tests for the logo image."""

    def setUp(self):
        utils.reset()

    def make_logo(self, name):
        """Creates a test with a given logo image."""
        path = os.path.join("tests", "images", "logo", f"{name}.jpg")
        atform.add_logo(path)
        self.make_test(
            preconditions=[
                "Verify the logo has a red border.",
                "Verify the shape in the middle is a circle.",
                "Verify the logo abuts the left margin.",
                "Verify the bottom of the logo clears the top of the first section.",
            ]
        )

    def test_full_size(self):
        """Verify appearance of a logo that is both maximum height and width."""
        self.make_logo("full")

    def test_full_width(self):
        """Verify appearance of a logo that is maximum width."""
        self.make_logo("width")

    def test_full_height(self):
        """Verify appearance of a logo that is maximum height."""
        self.make_logo("height")

    def test_small(self):
        """Verify appearance of a logo smaller than the maximum height and width."""
        self.make_logo("small")


class Copyright(Base, unittest.TestCase):
    """Tests for copyright notices."""

    def setUp(self):
        utils.reset()

    def make_test(self):
        """Fills the first page so the bottom margin can be verified."""
        super().make_test(procedure=["foo"] * 30)

    def test_single_line(self):
        """Verify appearance of a single-line copyright notice."""
        atform.add_copyright("\u00a9 Spam Eggs")
        self.make_test()

    def test_multi_line(self):
        """Verify appearance of a multi-line copyright notice."""
        atform.add_copyright(
            """
            Lorem ipsum odor amet, consectetuer adipiscing elit. Quis platea est
            non, volutpat vulputate luctus nullam. Dolor ligula rhoncus,
            malesuada nascetur senectus donec erat? Adipiscing et dignissim
            euismod cursus rutrum morbi parturient tempor elit. Nec imperdiet
            dictum lobortis, tristique commodo quis imperdiet suscipit ornare.
            Cubilia ligula id consectetur mattis duis elit tristique dis. Mus
            hac proin quis bibendum sapien ultrices erat.
            """
        )
        self.make_test()


class CachePageCount(Base, unittest.TestCase):
    """Tests for the cached page count."""

    # add_test() arguments to produce a three-page document.
    TEST_ARGS = {"procedure": ["step"] * 60}

    @patch("atform.cache.load", return_value={})
    def test_no_cache(self, mock):
        """Confirm correct page count(3) when no cache is available."""
        self.make_test(**self.TEST_ARGS)

    @patch("atform.cache.load", return_value={(1,): {"page count": 1}})
    def test_stale_low(self, mock):
        """Confirm correct page count(3) when the cached page count is too low."""
        self.make_test(**self.TEST_ARGS)

    @patch("atform.cache.load", return_value={(1,): {"page count": 99}})
    def test_stale_high(self, mock):
        """Confirm correct page count(3) when the cached page count is too high."""
        self.make_test(**self.TEST_ARGS)

    @patch("atform.cache.load", return_value={(1,): {"page count": 3}})
    def test_correct(self, mock):
        """Confirm correct page count(3) when the cached page count is right."""
        self.make_test(**self.TEST_ARGS)
