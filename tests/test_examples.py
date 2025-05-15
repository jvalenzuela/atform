# This module executes examples from the documentation.


from tests import utils
import os
import shutil
import subprocess
import sys
import unittest


# Path to the example scripts, relative to the repository root.
INPUT_PATH = os.path.join("doc", "source", "examples")

# List of all files in the examples directory, including supporting files
# that may not be Python scripts.
SRC_FILES = [entry.name for entry in os.scandir(INPUT_PATH) if entry.is_file()]

# Scripts to exclude from running.
EXCLUDE = set(
    [
        # These scripts are imported, not standalone.
        "button.py",
        "switch.py",
    ]
)

# Folder relative to the repository root where examples will be executed
# and resulting output will appear.
OUTPUT_PATH = "example_output"


def setUpModule():
    # Remove output from previous runs.
    shutil.rmtree(OUTPUT_PATH, ignore_errors=True)


def load_tests(loader, tests, pattern):
    """
    Overrides the default test discovery to create a separate TestCase
    for each example script.
    """
    scripts = set([f for f in SRC_FILES if f.endswith(".py")])
    scripts.difference_update(EXCLUDE)

    suite = unittest.TestSuite()

    # Add a TestCase for each script.
    for script in scripts:

        # Create the TestCase class name using the script file name
        # with the '.py' extension removed.
        name = os.path.splitext(script)[0]

        # Create a TestCase subclass dedicated to this script.
        cls = type(name, (Example,), {"script": script})

        tests = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
        suite.addTests(tests)

    return suite


class Example(unittest.TestCase):
    """Base class for a test case executing a single script."""

    def setUp(self):
        utils.reset()

    def test_example(self):
        with ExampleRunner(self.script) as runner:
            runner.run()


class ExampleRunner(object):
    """Context manager for running a single example script."""

    def __init__(self, script):
        self.script = script

    def __enter__(self):
        """
        Initializes an output directory matching the target script name
        under OUTPUT_PATH where the script will be run.
        """
        target_dir = os.path.join(OUTPUT_PATH, self.script)
        os.makedirs(target_dir)

        # Populate the directory with everything from the input path.
        # All files are copied, not just the target script, because
        # some examples need additional files in addition to the
        # target script itself.
        [
            shutil.copyfile(os.path.join(INPUT_PATH, f), os.path.join(target_dir, f))
            for f in SRC_FILES
        ]

        return self

    def run(self):
        """Executes the target script."""
        args = [
            sys.executable,  # System python executable.
            self.script,
        ]

        # PYTHONPATH is set to the current working directory(the repository
        # root) so the module can be imported when running scripts in the
        # output directories.
        env = dict(os.environ)
        env["PYTHONPATH"] = os.getcwd()

        # The target script will be run from within its dedicated output
        # path.
        cwd = os.path.join(os.getcwd(), OUTPUT_PATH, self.script)

        subprocess.run(args, env=env, cwd=cwd).check_returncode()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Cleans up the directory used to run the script by removing
        source files copied from INPUT_PATH when the directory was initalized,
        leaving only the output from the target script.
        """
        [os.remove(os.path.join(OUTPUT_PATH, self.script, f)) for f in SRC_FILES]
