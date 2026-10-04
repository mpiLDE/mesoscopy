.. _installation:

Installation
============

mesoscoPy is a Python program with a graphical interface. It runs on Windows, macOS and Linux and needs **Python 3.14 or
newer**. The simplest way to get a working installation is a dedicated *conda* environment: the file ``environment.yml`` of
the repository lists what the program needs: QCoDeS, Qt, NumPy, Matplotlib, SciPy and PyYAML. The drivers of some instruments
are optional and are installed separately (see below).

.. contents:: On this page
   :local:
   :depth: 1

1. Install a conda distribution
-------------------------------

Install `Miniforge <https://github.com/conda-forge/miniforge>`_ (recommended) or Anaconda, then open a terminal. On
Windows, use the *Miniforge Prompt* (or *Anaconda Prompt*) that the installer adds to the Start menu.

2. Get mesoscoPy
----------------

Download the latest release from `the releases page <https://github.com/julienbarrier/mesoscopy/releases>`_ and unpack it,
or clone the repository (it can be less stable than a release):

.. code:: bash

   git clone https://github.com/mpilde/mesoscopy.git
   cd mesoscopy

3. Create the environment
-------------------------

From the ``mesoscopy`` folder:

.. code:: bash

   conda env create -f environment.yml
   conda activate mesoscopy

This creates an environment called ``mesoscopy``. You activate it (``conda activate mesoscopy``) every time you open a new
terminal, before using the program.

4. Install the program
----------------------

With the environment activated, still in the ``mesoscopy`` folder:

.. code:: bash

   pip install .

This installs mesoscoPy and the ``mesoscopy`` command. If you want to change the code and see the changes at once, use
``pip install -e .`` (an *editable* install) instead.

5. Drivers and VISA, for the instruments that need them
-------------------------------------------------------

The environment is the bare minimum to run the program. Instruments may need more, which you install in the same environment
(``conda activate mesoscopy`` first):

**Zurich Instruments MFLI** (and the other drivers of the QCoDeS contrib package)
   .. code:: bash

      pip install "zhinst>=26.7.2" "zhinst-qcodes>=0.8.1" "qcodes_contrib_drivers>=0.24.0"

   or ``pip install ".[zurich]"`` from the ``mesoscopy`` folder. The MFLI is reached through the *LabOne* data server, which you
   install from Zurich Instruments.

**VISA instruments** (GPIB, USB, serial, network)
   QCoDeS installs PyVISA, which needs a VISA backend. Either install the VISA library of your instrument manufacturer, for
   example `R&S VISA <https://www.rohde-schwarz.com/applications/r-s-visa-application-note_56280-148812.html>`_ or NI-VISA
   (needed for **GPIB** and **USB**), or install the pure-Python backend, enough for instruments on a network or a serial port:
   ``conda install pyvisa-py pyserial`` (or ``pip install ".[visa]"``).

On Linux, tell PyVISA where a VISA library is, in ``~/.pyvisarc``:

.. code:: text

   [Paths]

   VISA library: /usr/lib/librsvisa.so

See the `PyVISA documentation <https://pyvisa.readthedocs.io/en/latest/introduction/configuring.html>`_ for the details. The
simulated instruments of :ref:`the quick overview <quickstart>` need none of this.

6. Start the program
--------------------

With the environment activated:

.. code:: bash

   mesoscopy

A window opens. If you have no hardware at hand, :ref:`the quick overview <quickstart>` shows how to try every tab on simulated
instruments.

Updating
--------

.. code:: bash

   cd mesoscopy
   git pull
   conda env update --file environment.yml --prune
   pip install --upgrade .

``--prune`` removes what the environment file does not list, so install the optional packages of step 5 again if you use them.

Something does not work?
------------------------

``mesoscopy: command not found``
   The environment is not activated (``conda activate mesoscopy``), or ``pip install .`` was not run in it.

``ModuleNotFoundError`` when starting
   Update the environment (see above). If the message names a driver package (``zhinst``, ``qcodes_contrib_drivers`` ...), it is one
   of the optional ones of step 5.

The window opens but an instrument cannot be loaded
   See :ref:`the Instruments tab <instruments>` and :ref:`the station file <station_file>`: the message under the
   buttons says what failed (a wrong address, a missing VISA library, an instrument that is already in use ...).
