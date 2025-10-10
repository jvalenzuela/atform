# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import pathlib
import shutil
import sys
import tomllib

# Update import path to locate atform modules.
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
import atform
import atform.version

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Load the top-level project configuration.
with open(os.path.join("..", "..", "pyproject.toml"), "rb") as f:
    config = tomllib.load(f)

project = config["project"]["name"]
copyright = "2024, Jason Valenzuela"
author = ""
release = atform.version.VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = []

rst_prolog = f"""
.. |project_name| replace:: {project}
.. |max_logo_width| replace:: {atform.image.MAX_LOGO_SIZE.width}
.. |max_logo_height| replace:: {atform.image.MAX_LOGO_SIZE.height}
.. |max_step_image_width| replace:: {atform.procedure.MAX_IMAGE_SIZE.width}
.. |max_step_image_height| replace:: {atform.procedure.MAX_IMAGE_SIZE.height}
.. |cache_filename| replace:: :file:`{atform.cache.FILENAME}`
.. |idlock_filename| replace:: :file:`{atform.idlock.FILENAME}`
"""

numfig = True

autodoc_typehints = "none"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    "extraclassoptions": "oneside",
    "pointsize": "12pt",
    "printindex": "",  # Exclude index in PDF output.
    "maketitle": r"\atformtitle",
    "preamble": r"""
    \usepackage{embedfile} % For attaching examples.
    \setlength{\headheight}{15pt}
    \usepackage{changelog}
    \usepackage{title}
    """,
}

latex_additional_files = [
    "changelog.sty",
    "title.sty",
    "images/python-powered.eps",
]


# Example files that will not be embedded in the output PDF.
EXCLUDE_FROM_EMBED = [
    "snip.py",
]


def add_example_embeds(app, config):
    """Adds commands to latex_elements to embed example files.

    Generating these commands requires listing the source directory,
    which requires the Sphinx application object, hence the reason
    these are added via an event callback instead of directly in the
    latex_elements definition.
    """
    global latex_elements
    path = os.path.join(app.srcdir, "examples")
    files = set([e.name for e in os.scandir(path) if e.is_file()])
    files.difference_update(EXCLUDE_FROM_EMBED)
    cmds = ["\\embedfile[filespec={0}]{{examples/{0}}}".format(f) for f in files]
    latex_elements["atendofbody"] = "\n".join(cmds)


def copy_examples(app, exception):
    """
    Copies all example files to the LaTeX output path so they can be
    embedded into the output PDF.
    """
    src = os.path.join(app.srcdir, "examples")
    dst = os.path.join(app.outdir, "examples")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)


def setup(app):
    app.connect("config-inited", add_example_embeds)

    # Copying examples into the build folder after the build is finshed
    # works because the Sphinx build only generates the LaTeX source files;
    # running LaTeX, which reads these copies, to construct the PDF is
    # actually part of the make process that runs after Sphinx is
    # completely finished.
    app.connect("build-finished", copy_examples)
