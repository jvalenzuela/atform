This document contains information relevant for package development and
maintenance; refer to the main README.md for end user documentation.


Prerequisites
=============

Items required to build a release, separate from those listed in
pyproject.toml:

- LaTeX, for building PDF manual with Sphinx.


Release Procedure
=================

- Checkout a new branch to test the new release.

- Increment the VERSION constant in atform/version.py.

- Add an entry describing the new version in doc/source/changelog.sty.

- Commit changes from steps 1 and 2.

- Push the new release branch to GitHub.

- Create a virtual environment for each Python minor version and
  dependency listed in pyproject.toml. Preferably repeat with other
  operating systems.

- Evaluate the output files in pdf/ and example_output/ from one run
  of unit tests.

- Tag the commit to be released as "release/major.minor".

- Create a new git worktree with the release tag checked out.

- Switch to a Python 3.11 environment with the following packages:
    * build
    * twine

- Build the distribution:

     python -m build --wheel

- Inspect the PDF manual in build/latex/, verifying the new version appears
  correctly in the release history.

- Upload the package to TestPyPI:

     twine upload --repository testpypi dist/*

- Verify the package at https://test.pypi.org/project/atform.

- Create a new virtual environment for each Python minor version listed
  in pyproject.toml, and confirm the package installs successfully from
  TestPyPI:

     pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ atform

- Push tags to GitHub.

- Create a new GitHub release for the new tagged commit.

- Upload the whl in dist/ and PDF manual in build/latex/ to the new GitHub
  release.

- Upload the package to PyPI:

     twine upload dist/*


Docstring Format
================

Docstrings for items accessible via the public API shall be in Google
Style. This style was chosen to yield the best results in not only the
manual as formatted by Sphinx, but also IDE calltips. Some IDEs
can display formatted docstrings, while others simply dislay plain text;
the Google style renders the best results in both cases.

https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html
