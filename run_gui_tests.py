"""
This script launches the interactive GUI unit tests. These tests require
user interaction, so they are located in a module named to prevent them from
running during normal test discovery. See tests/gui/igtest.py for details.
"""

import unittest


# Configure the runner so all testing is aborted upon first failure.
runner = unittest.TextTestRunner(failfast=True)

loader = unittest.TestLoader()
suite = loader.discover(".", pattern="igtest*")
runner.run(suite)
