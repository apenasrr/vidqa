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
* File names be less than 150 chars
* Videos are in mp4 format and h264/aac codecs

Usage
-----

**To use vidqa in CLI mode**

Unique mode to apply to a folder, generating one log file

.. code-block:: text

    $ vidqa -i "paste_a_folder_path" -m unique

batch mode to apply to a parent folder generating a different log file for each subfolder

.. code-block:: text

    $ vidqa -i "paste_a_folder_path" -m batch

Use by defining folder destination of the Metadata Report and Temporary Folder of Converted Videos

.. code-block:: text

    $ vidqa -i "paste_a_folder_path" -m unique -fd "c://my_temp_folder"

**To show or change encode video flags in CLI mode**

Show actual flags

.. code-block:: text

    $ vidqa flags

CRF - Constante Rate Frame. Stable quality. Default 20 for minimal loss.

.. code-block:: text

    $ vidqa flags --crf 23

maxrate - maximum bitrate peak in a second. Default 2 (MiB) to flow in slow connection stream.

.. code-block:: text

    $ vidqa flags --maxrate 3

folder_destination - Default folder where converted temporary reports and videos should be stored

.. code-block:: text

    $ vidqa flags -fd "c://my_temp_folder"

default_destination - Activates the default folder

.. code-block:: text

    $ vidqa flags -dd 1 # 0 to deactivate


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
