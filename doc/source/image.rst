.. _image:

Images
======

Graphical content included in the test document output, such as with
the :py:func:`atform.add_logo` or :py:func:`atform.add_test` API functions,
are stored in separate files and referenced by a path pointing to the source
image file.
Images must be either JPEG or PNG format. As a general rule,
photographs or scans are best served by JPEG, while PNG is better for
screenshots or diagrams.

Both image formats support optional metadata
specifying DPI, which is required by |project_name| to determine the size
of the image
in the output. A typical minimum is 300 DPI; lesser values may result
in poor image quality while higher values increase file sizes and
processing time.

|project_name| will not scale or crop
any image; the onus is on the user to construct images suitable for
presentation within the allowable area.
The maximum image size varies based on where the image is used, and is
listed in the relevant API documentation.
