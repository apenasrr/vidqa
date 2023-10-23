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

* Videos are in mp4 format and h264/aac codecs with audio channel up to 2
* File path length be less than 240 chars
* File names length be less than 150 chars

Quality assurance made effortless! `Click here`_ to watch a tutorial video and see how VIDQA can enhance the quality of your audiovisual content.

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

folder_log - Parent log folder where stores individual log folders for each project. Default = None.

.. code-block:: text

    $ vidqa flags -fl "c://my_temp_folder"

default_log - Activates the default parent log folder. Default = 0.

.. code-block:: text

    $ vidqa flags -dl 1 # 0 to deactivate

corrupt_del - Flag to allow delete corrupted videos from the project folder. Default = 1.

.. code-block:: text

    $ vidqa flags -cd 1

corrupt_bkp - Flag to allow do backup corrupted videos to the project log folder. Default = 1.

.. code-block:: text

    $ vidqa flags -cb 1


max_path = Maximum length that each file path is allowed to be. Default = 240.

.. code-block:: text

    $ vidqa flags -mp 230

max_name = Maximum length that each file name is allowed to be. Default = 150.

.. code-block:: text

    $ vidqa flags -mn 100

move_done = Flag to allow project to be moved after optimization (1 for allowed, 0 for disallowed). Default = 0.

.. code-block:: text

    $ vidqa flags -md 1

folder_destination = Folder where projects should be moved after optimization. Default = None.

.. code-block:: text

    $ vidqa flags -fd "c://optimized_projects"


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Click here`: https://www.youtube.com/watch?v=9cMFngtzpkY