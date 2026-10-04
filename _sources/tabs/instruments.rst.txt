.. _instruments:

Instruments tab
===============

The Instruments tab connects mesoscoPy to your instruments. You choose a :ref:`station file <station_file>`, load it, and then
load the instruments it describes.

.. figure:: /_static/img/instruments_loaded.png
   :alt: The Instruments tab with three connected instruments
   :width: 100%

   Three instruments connected. The coloured dots show that they answer.

.. contents:: On this page
   :local:
   :depth: 1

Loading a station
-----------------

Under *Station*:

1. **Browse...** to the folder that holds your station files. The drop-down below lists every ``*.station.yaml`` file of the
   folder.
2. Choose the file and click **Load Station**. This only *reads* the file: nothing is connected yet. The instruments it
   describes appear in the *Instruments to Load* list, and the ones you had loaded the last time you used this file are
   already selected.

.. figure:: /_static/img/instruments_station.png
   :alt: The Instruments tab after loading a station file
   :width: 100%

   After **Load Station**: the instruments of the file are listed, none is connected yet.

If the file cannot be read, the reason (usually a YAML syntax error) is shown under the buttons. See
:ref:`the station file <station_file>` for how to write one. Loading another station while instruments are connected keeps
the instruments whose entry is identical in the new file (same driver, address, presets and aliases) and disconnects the others.

Loading the instruments
-----------------------

Select the instruments in *Instruments to Load* (click, or Shift-click for several) and click **Load Selected Instruments**.
mesoscoPy imports each driver and connects. The instrument moves to *Connected instruments*; the parameters that the station
file declared as aliases appear in :ref:`the Parameter explorer <parameter_explorer>` as experiment parameters, and the tabs
that need instruments open.

If an instrument cannot be loaded, the message under the list says why (a wrong address, a missing driver package, a device
that is busy). The other instruments are still loaded.

The connected instruments
-------------------------

Each connected instrument shows its model, its serial number and a **coloured dot**:

- **green**: the instrument answered the last check (a ``get_idn`` request, repeated every few seconds in the background; the
  readings of :ref:`the Monitor <monitor>` count as a check too);
- **red**: it did not answer. Hover over the dot for the time of the last check and the error.

An instrument that is in use by a measurement is not asked: the check comes back when it is free.

The buttons under the list:

**Update Snapshot of Selected**
   Reads every parameter of the selected instruments again. QCoDeS stores the *last known* values in the snapshot saved with
   each run, so do this after you changed something on the front panel of an instrument.

**Reconnect Selected**
   Appears when an instrument stops answering. It closes the instrument and loads it again from the station file. The
   experiment parameters changed by the program that belong to it are first brought to 0 (see :ref:`safety`), unless the
   instrument is not answering.

**Disconnect Selected**
   Closes the instrument and removes it from the station. The experiment parameters of that instrument that the program has
   changed are first ramped to 0, at their maximum ramp rate, with a progress window. It is refused while a measurement or
   another action uses the instrument.

Right-click an instrument for a menu with **Update snapshot**, **Disconnect**, and **Save state ... to file** and **Restore
state ... from file / from a run**, which write and read all the parameters of the instrument.

The instrument panel
--------------------

Select a single instrument and a panel opens on the right with three pages, chosen by the buttons at the bottom:

**Command log**
   The commands that QCoDeS sent to the instrument and the answers it got, as they happen. It helps to see what a driver
   really does. Not every driver logs its commands (a simulated instrument for instance).

   .. figure:: /_static/img/instruments_log.png
      :alt: The command log of an instrument
      :width: 100%

**Raw command**
   Type a command, then **Ask** (send it and read the answer) or **Write** (send it). Only for VISA instruments. Raw commands
   go straight to the instrument: **the safe limits, the validators and the ramp rates do not apply**, and they are refused
   while a measurement runs.

**Snapshot**
   All the parameters of the instrument with their last known values.

   .. figure:: /_static/img/instruments_snapshot.png
      :alt: The snapshot of an instrument
      :width: 100%
