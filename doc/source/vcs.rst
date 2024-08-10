.. _vcs:

Version Control
===============

Like any other important content, test documentation should be maintained
within a formal version control system. This becomes especially important
as the documentation grows in size, undergoes revision,
and is distributed among different parties. For these, and many other reasons,
it is *highly* recommended to place scripts and related data
sources into a version control system.

Many version control systems are available, however, the features
described in this section are only compatible with the git version
control system. Aside from details described in :ref:`install`,
git does not require any special configuration or operation
for use with |project_name|. Other version control systems can be used,
or none at all, but these features will be dormant.

How to use a version control system, git or otherwise, is beyond the
scope of this manual; users should refer to the documentation specific
to the system in use.

The version control functions of |project_name| are automatically
activated if git is
installed and scripts are placed in a git repository.
When version control is enabled
|project_name| will apply the following marks to output PDF documents:

* A :literal:`DRAFT` watermark if the working directory contains *any*
  uncommitted changes.

* A :literal:`Document Version` field in the footer containing the git
  SHA1 of the current HEAD if the working directory is clean, i.e.,
  no uncommitted changes.

This manual does not include any examples specific to version control
because no changes are needed to enable or configure it.
Copying any of the existing examples into a git repository will
demonstrate version control functionality.
There is, however, a sample :file:`.gitignore` file attached to this manual
to assist in setting up a git repository for |project_name| scripts.
