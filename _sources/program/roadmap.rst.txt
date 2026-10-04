.. _roadmap:

Limitations and roadmap
=======================

This page says what mesoscoPy does **not** do yet, so that you know before you plan an experiment. The first part lists the
limitations of the present version (0.2.0). The second part lists what is planned or wished for. It is a list of intentions, not
a promise and not a schedule; what is done is in :ref:`the changelog <changelog>`.

.. contents:: On this page
   :local:
   :depth: 2

Limitations of this version
---------------------------

Measuring
^^^^^^^^^

- **One measurement at a time.** A measurement takes every instrument of the station: two measurements cannot run in parallel, and
  while one runs, setting a value, loading a snapshot or sending a raw command is refused.
- **A measurement cannot resume in the middle of a sweep.** After a crash, a power cut or a stop, a run starts again from its
  beginning. The data it had written stays in the database, and an interrupted queue can be restored, but the interrupted item
  runs again from its start (see :ref:`queue`).
- **Up to four sweep axes**, and the points of a sweep are all known before it starts. A sweep cannot adapt to what it measures
  (a refined step near a peak, an axis that follows a feature).
- **The time estimate leaves out the instruments.** It counts the delays and the ramps; the time the instruments take to answer
  at each point, and the overheads, are not included, so a long measurement takes longer than announced.
- **Parameter types.** Numbers, complex numbers and traces (an array with its own axis) are measured and plotted. Text parameters
  are skipped by the plot. QCoDeS' ``MultiParameter`` and ``ArrayParameter`` are not specially handled and are untested: give an
  array parameter its axis as a trace, or use a driver parameter with setpoints.
- **Raw commands** can be sent only to VISA instruments, and they bypass the safe limits (see :ref:`safety`).

Plots and analysis
^^^^^^^^^^^^^^^^^^

- **The live plot of a map is a stack of curves**, not a colour map: you see the latest sweep of the inner axis, with the previous
  sweeps faded behind it. Structure that appears across the outer axis is hard to see until the run is finished; analyse the
  finished map with QCoDeS' own tools (``plot_dataset``, or the data exported after the run).
- **There are no analysis tools in the program** (line cuts, normalisation, fits). It plots, takes a derivative, and picks values
  from curves; the analysis is done outside, on the database or on the exported files.
- **The Data tab does not plot** the runs of the explorer. It lists, tags, annotates, compares and reloads them.
- **No manual export of a past run.** The data is exported automatically after each run if you ask for it in the advanced settings
  of the measurement; a run that was not exported then cannot be exported from the explorer, and runs cannot be copied from one
  database to another. Use QCoDeS (``dataset.export()``, ``extract_runs_into_db``) for that.

Instruments and stations
^^^^^^^^^^^^^^^^^^^^^^^^

- **The station file is written by hand.** There is no editor, no validator and no *Reload* button: change the file, then load the
  station again. An error shows when the file is loaded.
- **No discovery.** The program does not list the VISA resources or the Zurich Instruments devices that it can see, and does not test a
  connection before loading an instrument: you need to know the address.
- **Instruments are connected for the session only,** and an instrument that stops answering is shown by a red dot but is not
  reconnected by itself (use **Reconnect Selected**).
- **Recipes name instruments through experiment parameters.** A recipe written for one setup has to be edited for another
  setup whose parameters have other names.
- **Drivers.** The program ships drivers for the Oxford Instruments ITC503 and Mercury iTC and the Montana Instruments Cryostation,
  and simulated instruments. Everything else comes from the QCoDeS drivers or from the QCoDeS contrib drivers, with their
  possibilities and their limits.

Monitoring and notification
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **No notifications.** An alarm, the end of a measurement or the end of a queue is shown in the program and written to the log,
  but no e-mail, message or push notification is sent.
- **No remote view.** The QCoDeS web monitor is not offered, so you cannot follow a run from a phone.
- **While a measurement runs, the Monitor does not read the instruments itself**: the measurement hands it the values, at most
  once per point (see :ref:`monitor`).

Data
^^^^

- **Databases are closed at 750 MB**, and the next measurement starts the next database of the series.
- **One folder, one sample.** The database folder and the sample name of the Data tab apply to the whole program at a given
  time; several samples at once need several instances of the program.

Roadmap
-------

Planned or wished for, by tab. The order inside a group says nothing about the order of work.

Data tab
^^^^^^^^

- Filter and sort the runs of the explorer.
- Export a selected run (CSV, NetCDF) and copy selected runs into another database.
- Plot a finished run in the explorer with the same plot panel as the live plot.
- More metadata on a run (operator, sample identifier) next to the tag and the notes.

Instruments tab
^^^^^^^^^^^^^^^

- **Load all instruments** and **Reload station file** buttons, and a validator that shows the errors of a station file where they are.
- Discovery of the VISA resources and of the Zurich Instruments devices, with *Add to station*, and a connection test before loading
  (is the host reachable, is the port open, is the device already in use).
- A simulation mode per instrument, using a simulated driver, to prepare a measurement without the hardware.
- **Instrument roles** ("master lock-in", "gate source"), so that recipes and defaults refer to a role and not to a name.

Parameter explorer tab
^^^^^^^^^^^^^^^^^^^^^^

- Show the modules of an instrument (QCoDeS ``InstrumentModule``) as sections of the table; the group parameters are already shown
  together.
- Edit more of what QCoDeS offers for a parameter: ``post_delay``, validators, parsers; test and support ``MultiParameter`` and
  ``ArrayParameter`` as measured parameters.

Measurement tab
^^^^^^^^^^^^^^^

- A **colour-map view** of a map in the live plot, with a slice selector, rows added as they arrive and colour limits that follow;
  line cuts, normalisation and fits in the plot.
- Picking values on the plot, further: a fitted peak position instead of the raw maximum, a centre and a span, a click on a map to
  set both axes, undo of the last filled value.
- A queue step that sets a parameter to the **extremum of the last run** by itself (run-to-run feedback without a click).
- A time estimate learnt from the previous runs (the measured time per point of a recipe), used for the run and for the queue total.
- Sweeps as a function of time, and adaptive sweeps.
- Use the streaming of the Zurich Instruments devices instead of one reading per point, for faster lock-in sweeps.
- More of QCoDeS' ``Measurement`` API for people who need it: custom parameters, callbacks, actions after the run.

Queue tab
^^^^^^^^^

- Resume a measurement in the middle of a sweep after an interruption.
- Notifications (e-mail, a message, a push) when a measurement or the queue finishes, or an alarm goes off.

Monitor tab
^^^^^^^^^^^

- A web page, with the QCoDeS monitor, to watch the setup from a phone.
- Store the history of a parameter thinned out (the traces keep 24 hours of readings as they are).

Program
^^^^^^^

- A live plot built on a faster library (pyqtgraph) for very large maps and traces.
- A common plot component for the Measurement tab, the Monitor and the Data tab.

Ideas and bug reports
---------------------

Tell us what is missing, or what does not work, on `the issue tracker of the project
<https://github.com/mpilde/mesoscopy/issues>`_.
