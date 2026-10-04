.. _station_file:

Building the station file
=========================

The **station file** tells mesoscoPy which instruments you have, how to reach them and which of their parameters you want to
use. It is a text file in the YAML format, the one QCoDeS calls a *station configuration*. You write it once for a setup and
load it from :ref:`the Instruments tab <instruments>` every time you start the program.

.. contents:: On this page
   :local:
   :depth: 2

The basics
----------

- The file name must end with ``.station.yaml`` (``fridge.station.yaml``, ``dummy.station.yaml`` ...). The Instruments tab
  lists the files of that kind that it finds in the *station folder* you choose.
- Indent with **spaces** (two per level), never with tabs. A ``#`` starts a comment.
- The file has one top-level key, ``instruments``. Each entry below it describes one instrument and is named by you: that
  name is how the instrument appears in the program and in the database.

The smallest useful station file is this one, a simulated instrument that needs no hardware:

.. code:: yaml

   instruments:
     dummy_dac:
       type: qcodes.instrument_drivers.mock_instruments.DummyInstrument
       init:
         gates: [ch1, ch2, ch3, ch4]

Load it, and ``dummy_dac`` appears in the *Instruments to Load* list.

What an instrument entry contains
---------------------------------

``type``
   The Python path of the driver class, as you would import it: ``package.module.ClassName``. Drivers come from
   `QCoDeS <https://microsoft.github.io/Qcodes/>`_ (``qcodes.instrument_drivers...``), from the `QCoDeS contrib drivers
   <https://github.com/QCoDeS/Qcodes_contrib_drivers>`_ (``qcodes_contrib_drivers.drivers...``), from mesoscoPy itself
   (``mesoscopy.instrument.temperature`` has the Oxford Instruments ITC503 and Mercury iTC and the Montana Instruments
   Cryostation) or from a module of your own that Python can import.

``init``
   The arguments the driver needs to connect, exactly as its constructor asks for them: a VISA ``address``, a ``serial``
   number and ``host`` for a Zurich Instruments device, a ``gates`` list for the simulated instrument. The name you gave the
   entry is passed as the instrument's ``name``; do not repeat it.

``enable_forced_reconnect: true``
   Lets the instrument be loaded again when a previous session did not close it properly (QCoDeS would otherwise refuse
   because the name is still in use). It is on in the examples of this page.

``parameters``
   The **presets**: values QCoDeS sets, in the order you write them, as soon as the instrument is loaded. The key is the path of
   the parameter inside the instrument (``ch1``, ``oscs[0].freq``, ``sigouts[0].range``) and the value says what to do with
   it:

   .. code:: yaml

      parameters:
        ch1: {initial_value: 0.0, limits: [-5, 5]}
        sigouts[0].range: {initial_value: 10}

   ``initial_value`` sets the parameter at load time. ``limits: [min, max]`` makes QCoDeS refuse any value outside the
   range. ``step`` and ``inter_delay`` make QCoDeS change the parameter by at most ``step`` every ``inter_delay`` seconds.

``add_parameters``
   The **aliases**: short names for parameters that are deep in the instrument's tree. This is what you will use most.
   Every alias becomes an *experiment parameter* in :ref:`the Parameter explorer <parameter_explorer>`, named
   ``<instrument>_<alias>``, as soon as the instrument is loaded:

   .. code:: yaml

      add_parameters:
        Vtop: {source: ch1, unit: V, limits: [-2, 2], step: 0.1, inter_delay: 0.05}

   ``source``
      the path of the real parameter inside the instrument;
   ``unit``
      the unit shown in the program;
   ``limits``
      the **safe limits** of the experiment parameter: a sweep or a set beyond them is refused;
   ``step`` and ``inter_delay``
      the **maximum ramp rate**. ``step`` divided by ``inter_delay`` is the largest change per second: in the example, 0.1 V
      every 0.05 s is 2 V/s. Every set of that parameter, in a sweep or by hand, is made in steps of that size.

.. note::

   Put the safe limits and the ramp rate in the station file for every gate and every source. They are then the same each
   time you load the station, and a typing mistake in a sweep cannot send a dangerous voltage to the sample.

A parameter at the root of the station
--------------------------------------

An entry whose ``type`` is a QCoDeS *parameter* class instead of an instrument is a parameter that belongs to no instrument.
The usual one is a clock:

.. code:: yaml

   instruments:
     elapsed_time:
       type: qcodes.parameters.ElapsedTimeParameter

It is available in the Parameter explorer as soon as the file is loaded, and you can measure it like any other parameter.

A complete example without hardware
-----------------------------------

This is the file used by :ref:`the quick overview <quickstart>` (:download:`download it <_static/dummy.station.yaml>`):

.. literalinclude:: _static/dummy.station.yaml
   :language: yaml

``dummy_dac`` has four gates, two of which (``ch1`` and ``ch2``) start at 0 V and are aliased as ``Vtop`` and ``Vback`` with
their limits and ramp rates. ``dummy_dmm`` and ``dummy_scope`` are simulated meters whose readings follow the gates; their
``init`` has a ``source`` that names the instrument whose gates they read. The aliases give four experiment parameters:
``dummy_dac_Vtop``, ``dummy_dac_Vback``, ``dummy_dmm_signal`` and ``dummy_dmm_signal2``.

A lock-in amplifier
-------------------

A real instrument is described the same way. This is the beginning of the file for a Zurich Instruments MFLI that is used
for current-voltage measurements (the repository has the whole file, ``MFLI_IV.station.yaml``). Its driver needs the optional
Zurich Instruments packages of :ref:`the installation <installation>` (step 5):

.. code:: yaml

   instruments:
     mf6626:
       type: qcodes_contrib_drivers.drivers.ZurichInstruments.MFLI.MFLI
       init:
         serial: 'DEV6626'
         host: 'localhost'
         interface: '1GbE'
       enable_forced_reconnect: true
       parameters:
         oscs[0].freq: {initial_value: 1.0}
         sigins[0].diff: {initial_value: 1}
         sigins[0].range: {initial_value: 0.003}
         sigouts[0].range: {initial_value: 1}
         # the output switch is left OFF: switch it on yourself once the amplitude and the wiring are checked
         # sigouts[0].on: {initial_value: 1}
       add_parameters:
         freq: {source: "oscs[0].freq", unit: Hz}
         amplitude: {source: "sigouts[0].amplitudes[0].value", unit: V}

.. warning::

   Do not switch an output on from the ``parameters`` section unless you are sure of what is connected to it: a preset is
   applied every time the instrument is loaded, with nobody looking.

The paths such as ``oscs[0].freq`` are the ones of the driver (``instrument.oscs[0].freq``). To find them, load the instrument
and look in :ref:`the Parameter explorer <parameter_explorer>`: choose the instrument in *Component* and tick *Include
sub-components*; the *Parameter* column shows the full name of each parameter.

Instruments that use a VISA address
-----------------------------------

GPIB, USB, serial and network instruments are reached through a VISA address, which goes in ``init``. Replace the address
and the driver by those of your instrument (the QCoDeS documentation lists the drivers):

.. code:: yaml

   instruments:
     lockin:
       type: qcodes.instrument_drivers.stanford_research.SR830.SR830
       init:
         address: 'GPIB0::8::INSTR'
       add_parameters:
         time_constant: {source: time_constant, unit: s}
         X: {source: X, unit: V}

     smu:
       type: qcodes.instrument_drivers.Keithley.Keithley_2450.Keithley2450
       init:
         address: 'USB0::0x05E6::0x2450::04412345::INSTR'

To list the addresses that your VISA library sees, run ``python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"``
in the environment.

The repository also has ``docs/station_templates.yaml``: templates for other instrument families (an MFLI used as a slave
lock-in, the SR830, the SR860, Keithley source meters and the SIM928) that you can copy into your own file.

Checking the file
-----------------

1. In the Instruments tab, choose the folder and the file and click **Load Station**. This reads the file: a syntax error
   (wrong indentation, a missing colon) is shown under the buttons, and the instruments appear in *Instruments to Load*.
2. Select an instrument and click **Load Selected Instruments**. This imports the driver and connects: an error here, shown
   under the *Connected instruments* list, usually comes from the ``type`` (a typo in the path, a package that is not
   installed) or from ``init`` (a wrong address or serial number).
3. Open the Parameter explorer and check that your aliases are listed as experiment parameters, with the right safe range and
   maximum ramp rate.

Common problems
---------------

The file is not listed
   Its name does not end with ``.station.yaml``, or it is not in the folder you chose.

``Another instrument has the name`` when loading
   A previous session left the instrument open. Add ``enable_forced_reconnect: true`` to its entry.

An alias is missing from the experiment parameters
   Its ``source`` path is wrong (the instrument was loaded but the alias could not be built), or you removed it from the
   Parameter explorer; the **Restore parameters from the station file** button brings it back.

The instrument loads but does not answer
   The address is wrong or another program (or a second instance of mesoscoPy) is using the instrument. The coloured dot next
   to it in the Instruments tab turns red.
