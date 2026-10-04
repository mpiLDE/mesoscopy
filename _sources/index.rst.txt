.. mesoscoPy documentation master file.

mesoscoPy
=========

mesoscoPy is a graphical program to run electron-transport experiments. It controls the instruments of a measurement setup
(sources, lock-in amplifiers, meters, cryostat and magnet) through `QCoDeS <https://microsoft.github.io/Qcodes/>`_, runs
sweeps and queues of measurements, shows them live, and stores everything in QCoDeS databases.

.. figure:: /_static/screenshot.png
   :alt: The main interface of mesoscoPy
   :width: 100%

This documentation follows the program: after the quick overview there is one page for each tab, in the order you use them.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   installation
   quickstart
   station_file

.. toctree::
   :maxdepth: 1
   :caption: The tabs

   tabs/data
   tabs/instruments
   tabs/parameter_explorer
   tabs/measurement
   tabs/queue
   tabs/monitor

.. toctree::
   :maxdepth: 1
   :caption: The whole program

   program/settings
   program/safety
   program/roadmap

.. toctree::
   :maxdepth: 1
   :caption: More

   changelog

License
-------

.. include:: ../LICENSE
