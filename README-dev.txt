This document contains information relevant for package development and
maintenance; refer to the main README.md for end user documentation.


Prerequisites
=============

Dependencies other from those listed in pyproject.toml:

- Sphinx, for building PDF manual.
- LaTeX, for building PDF manual with Sphinx.
- twine, for uploading release to PyPI.


Release Procedure
=================

- Checkout a new branch to test the new release.

- Increment the VERSION constant in atform/version.py.

- Add an entry describing the new version in doc/source/changelog.sty.

- Commit changes.

- Tag the commit to be released as "release/major.minor".

- Push the new release tag to GitHub and wait for the release action
  to complete.

- Execute the GUI unit tests by running the run_gui_tests.py script with each
  supported Python version.

- Download and inspect the PDF manual in the draft GitHub release,
  verifying the new version appears correctly in the release history.

- Download and visually inspect the output files in one of the
  unittest_output artifacts created by the release action.

- Download the distribution .whl from the draft GitHub release and
  upload it to TestPyPI:

     twine upload --repository testpypi <whl file>

  * If rebuilding a release due to a problem found after uploading to
    TestPyPI, rename the wheel to include a build tag:

    https://peps.python.org/pep-0427/#file-name-convention

- Verify the package at https://test.pypi.org/project/atform.

- Create a new virtual environment for each Python minor version listed
  in pyproject.toml, and confirm the package installs successfully from
  TestPyPI:

     pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ atform

- Publish the GitHub release.

- Upload the package to PyPI:

     twine upload <whl file>


Docstring Format
================

Docstrings for items accessible via the public API shall be in Google
Style. This style was chosen to yield the best results in not only the
manual as formatted by Sphinx, but also IDE calltips. Some IDEs
can display formatted docstrings, while others simply dislay plain text;
the Google style renders the best results in both cases.

https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html
