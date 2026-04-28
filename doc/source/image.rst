.. _image:

Images
======

Graphical content included in the test document output, such as with
the :py:func:`atform.add_logo` or :py:func:`atform.add_test` API functions,
is stored in separate files and referenced by a path pointing to the source
image file.
Images must be either JPEG or PNG format. As a general rule,
photographs or scans are best served by JPEG, while PNG is better for
screenshots or diagrams.

The maximum image size varies based on where the image is used, and is
listed in the relevant API documentation. |project_name| will use one of
the following methods to fit an image to the allowable area:

#. If the image fits as-is within the allowable area it will retain its
   original size.

#. If the image exceeds the maximum size it will be scaled to fit in the
   allowable area.

#. If the image file does not contain DPI metadata by which to calculate
   its physical size it will be scaled to the maximum allowable
   height or width.

Any scaling performed by |project_name| will retain the original aspect ratio.

.. note::

   Although |project_name| will scale images as necessary,
   images of excessive size or resolution will result in unnecessarily large
   PDF files.
