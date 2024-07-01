# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import pathlib
import re
import sys
import tomllib

# Update import path to locate testgen modules.
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
import testgen

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Load the top-level project configuration.
with open(os.path.join('..', '..', 'pyproject.toml'), 'rb') as f:
    config = tomllib.load(f)

# Extract the minimum required Python version from the project configuration.
requires_python = re.search(
    r"\d+(\.\d+)*",
    config['project']['requires-python']).group()

project = config['project']['name']
copyright = '2024, Jason Valenzuela'
author = ''
release = config['project']['version']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = []

rst_prolog = f"""
.. |requires_python| replace:: {requires_python}
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'extraclassoptions': 'oneside',
    'pointsize': '12pt',
    'printindex': '', # Exclude index in PDF output.
}
