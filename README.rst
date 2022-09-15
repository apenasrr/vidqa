=====
vidqa
=====


.. image:: https://img.shields.io/pypi/v/vidqa.svg
        :target: https://pypi.python.org/pypi/vidqa

.. image:: https://readthedocs.org/projects/vidqa/badge/?version=latest
        :target: https://vidqa.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Quality assurance for audiovisual collections


* Free software: MIT license
* Documentation: https://vidqa.readthedocs.io.

Features
--------

Ensures:

* File paths less than 250 characters
* File names be less than 100 chars
* Videos are in mp4 format and h24/aac codecs

Usage
-----

**To use vidqa in CLI mode**

Unique mode to apply to a folder, generating one log file

.. code-block:: text

    $ vidqa -i "paste_a_folder_path" -m unique

batch mode to apply to a parent folder generating a different log file for each subfolder

.. code-block:: text

    $ vidqa -i "paste_a_folder_path" -m batch

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
