"""One sweep dimension (axis) of a dond measurement: sweep class and its fields."""
import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QVBoxLayout, QWidget,
)
from qcodes.dataset import ArraySweep, LinSweep, LogSweep, TogetherSweep

from mesoscopy.core.array_expression import evaluate_array_expression
from mesoscopy.core.dond_options import clean_actions
from mesoscopy.ui.tabs.component_selector import ComponentSelector, is_settable_numeric
from mesoscopy.ui.tabs.ui_helpers import set_groupbox_title_bold

START_STOP_WIDTH, TOGETHER_WIDTH = 70, 50  # minimum widths of the Start and Stop fields (pixels)
SWEEP_CLASSES = ["LinSweep", "LogSweep", "ArraySweep", "TogetherSweep"]

# Fields shown for each sweep class (a field is a label and its input widget(s))
FIELDS_BY_CLASS = {
    "LinSweep": {"component", "start", "stop", "num", "delay"},
    "LogSweep": {"component", "start", "stop", "num", "delay"},
    "ArraySweep": {"component", "array", "delay"},
    "TogetherSweep": {"together1", "together2", "num", "delay"},
}


def _row(*widgets, stretch_index=None):
    """Horizontal container of widgets (zero margins), usable as one show/hide unit."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    for i, widget in enumerate(widgets):
        layout.addWidget(widget, 1 if i == stretch_index else 0)
    layout.addStretch(0 if stretch_index is not None else 1)
    return container


def _line_edit(text, placeholder=""):
    edit = QLineEdit(text)
    edit.setPlaceholderText(placeholder)
    return edit


class SweepDimensionBox(QGroupBox):
    """One axis of the measurement: pick a sweep class and fill its fields.

    ``get_sweep()`` returns the matching QCoDeS sweep object (LinSweep, LogSweep, ArraySweep
    or TogetherSweep), ready to be passed to ``dond``.

    ``changed`` is emitted whenever a field that influences the sweep is edited.
    """

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Sweep", parent)
        set_groupbox_title_bold(self)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # header: sweep class
        self.class_combo = QComboBox()
        self.class_combo.addItems(SWEEP_CLASSES)
        self.class_combo.currentIndexChanged.connect(self.update_visible_fields)
        header = QHBoxLayout()
        header.addWidget(QLabel("Sweep class:"))
        header.addWidget(self.class_combo)
        header.addStretch()
        layout.addLayout(header)

        self.fields = {}

        # sweep component (LinSweep, LogSweep, ArraySweep)
        self.component_selector = ComponentSelector(param_filter=is_settable_numeric, empty_text="No experiment parameters")
        self.fields["component"] = _row(QLabel("Sweep component:"), self.component_selector)

        # TogetherSweep: two components, each with its own start/stop
        self.together_selectors = []
        self.together_starts = []
        self.together_stops = []
        for n in ("1", "2"):
            selector = ComponentSelector(param_filter=is_settable_numeric, empty_text="No experiment parameters")
            start, stop = _line_edit("0.0", "Start value"), _line_edit("1.0", "Stop value")
            self.together_selectors.append(selector)
            self.together_starts.append(start)
            self.together_stops.append(stop)
            self.fields[f"together{n}"] = _row(
                QLabel(f"Sweep {n}:"), selector, QLabel(f"Start{n}:"), start, QLabel(f"Stop{n}:"), stop
            )

        # ArraySweep: Python expression, numpy available as np
        self.array_input = _line_edit(
            "np.linspace(0, 1, 101)",
            "Python expression, e.g. np.concatenate((np.linspace(0, 1, 51), np.linspace(1, 0, 51)))",
        )
        self.array_input.setToolTip("Python expression giving the sweep values. numpy is available as 'np'.")
        self.array_input.textChanged.connect(self.update_array_info)
        self.array_info = QLabel("")
        self.fields["array"] = _row(QLabel("Array:"), self.array_input, self.array_info, stretch_index=1)
        self.update_array_info()

        # start / stop / num points / delay
        self.start_input = _line_edit("0.0", "Start value")
        self.stop_input = _line_edit("1.0", "Stop value")
        self.num_input = QSpinBox()
        self.num_input.setMinimum(1)
        self.num_input.setMaximum(9999)
        self.num_input.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.num_input.setValue(101)
        self.num_input.setFixedWidth(self.num_input.fontMetrics().horizontalAdvance("99999") + 16)
        self.delay_input = _line_edit("0.6", "Delay in seconds")
        for edit in (self.start_input, self.stop_input):  # the values are typed and picked from the plot: room for many digits
            edit.setMinimumWidth(START_STOP_WIDTH)
        for edit in (*self.together_starts, *self.together_stops):
            edit.setMinimumWidth(TOGETHER_WIDTH)
        self.fields["start"] = _row(QLabel("Start:"), self.start_input)
        self.fields["stop"] = _row(QLabel("Stop:"), self.stop_input)
        self.fields["num"] = _row(QLabel("Num points:"), self.num_input)
        self.fields["delay"] = _row(QLabel("Delay (s):"), self.delay_input)

        layout.addWidget(self.fields["component"])
        layout.addWidget(self.fields["together1"])
        layout.addWidget(self.fields["together2"])
        layout.addWidget(self.fields["array"])
        params = QHBoxLayout()
        for key in ("start", "stop", "num", "delay"):
            params.addWidget(self.fields[key])
        params.addStretch()
        layout.addLayout(params)

        # the dond options of the axis (set in the advanced settings): read the parameter back after setting it, and
        # actions run right after each set (before the delay and the inner loop)
        self.get_after_set = False
        self.actions = []

        self.update_visible_fields()
        self._connect_change_signals()

    def _connect_change_signals(self):
        edits = [self.start_input, self.stop_input, self.delay_input, self.array_input,
                 *self.together_starts, *self.together_stops]
        for edit in edits:
            edit.textChanged.connect(self.changed)
        self.num_input.valueChanged.connect(self.changed)
        self.class_combo.currentIndexChanged.connect(self.changed)

    def pick_fields(self):
        """[(edit, text, selector)]: the Start and Stop fields now shown that the plot can fill in, with the selector of
        the component each one belongs to (a TogetherSweep has two of each)."""
        sweep_class = self.sweep_class()
        if sweep_class in ("LinSweep", "LogSweep"):
            return [(self.start_input, "Start", self.component_selector), (self.stop_input, "Stop", self.component_selector)]
        if sweep_class == "TogetherSweep":
            return [(edit, f"{word}{n + 1}", self.together_selectors[n])
                    for word, edits in (("Start", self.together_starts), ("Stop", self.together_stops))
                    for n, edit in enumerate(edits)]
        return []

    # ----- display -----
    def set_title(self, text):
        self.setTitle(text)

    def sweep_class(self):
        return self.class_combo.currentText()

    def update_visible_fields(self):
        """Show exactly the fields that the selected sweep class uses."""
        sweep_class = self.sweep_class()
        for key, widget in self.fields.items():
            widget.setVisible(key in FIELDS_BY_CLASS[sweep_class])
        hint = "Actual values (> 0); points are spaced logarithmically." if sweep_class == "LogSweep" else ""
        self.start_input.setToolTip(hint)
        self.stop_input.setToolTip(hint)

    def update_array_info(self):
        """Show the number of points (or the error) of the array expression."""
        try:
            array = evaluate_array_expression(self.array_input.text())
        except ValueError as e:
            self.array_info.setStyleSheet("color: #c00;")
            self.array_info.setText("invalid")
            self.array_info.setToolTip(str(e))
            return
        self.array_info.setStyleSheet("")
        self.array_info.setText(f"{len(array)} points")
        self.array_info.setToolTip(f"from {array[0]:g} to {array[-1]:g}")

    def set_root(self, components):
        """Fill all selectors with the experiment parameters ({name: parameter}); selections are kept if valid."""
        self.component_selector.set_root(components)
        for selector in self.together_selectors:
            selector.set_root(components)

    # ----- saving and restoring the fields -----
    def get_state(self):
        """The fields as plain data (JSON-compatible); components are given by their path."""
        return {
            "class": self.sweep_class(),
            "component": self.component_selector.path(),
            "start": self.start_input.text(),
            "stop": self.stop_input.text(),
            "num": self.num_input.value(),
            "delay": self.delay_input.text(),
            "array": self.array_input.text(),
            "together": [selector.path() for selector in self.together_selectors],
            "together_starts": [edit.text() for edit in self.together_starts],
            "together_stops": [edit.text() for edit in self.together_stops],
            "get_after_set": self.get_after_set,
            "actions": [dict(a) for a in self.actions],
        }

    def set_state(self, state):
        """Fill the fields from ``get_state()`` data (missing entries keep their value).

        Returns the problems: the components that are not available as experiment parameters.
        """
        self.get_after_set = bool(state.get("get_after_set", False))  # not in older states: the default
        self.actions = clean_actions(state.get("actions"))
        if state.get("class") in SWEEP_CLASSES:
            self.class_combo.setCurrentText(state["class"])
        for key, edit in (("start", self.start_input), ("stop", self.stop_input),
                          ("delay", self.delay_input), ("array", self.array_input)):
            if key in state:
                edit.setText(str(state[key]))
        if "num" in state:
            self.num_input.setValue(int(state["num"]))
        for edits, key in ((self.together_starts, "together_starts"), (self.together_stops, "together_stops")):
            for edit, text in zip(edits, state.get(key, [])):
                edit.setText(str(text))
        wanted = (
            [state.get("component")] if self.sweep_class() != "TogetherSweep" else state.get("together", [])
        )
        selectors = [self.component_selector] if self.sweep_class() != "TogetherSweep" else self.together_selectors
        problems = []
        for selector, path in zip(selectors, wanted):
            if path and not selector.set_path(path):
                problems.append(f"{path[0]} is not available as a sweep component")
        return problems

    def fill_missing_components(self, state):
        """Select, in the selectors that are still empty, the components of ``get_state()`` data (they may
        not have been available before). Returns how many could not be selected yet."""
        pairs = ([(self.component_selector, state.get("component"))] if self.sweep_class() != "TogetherSweep"
                 else list(zip(self.together_selectors, state.get("together", []))))
        unresolved = 0
        for selector, path in pairs:
            if path and not selector.path() and not selector.set_path(path):
                unresolved += 1
        return unresolved

    def axis_estimate(self):
        """(points, delay) of this axis from the fields, or None while they are incomplete or invalid."""
        try:
            delay = float(self.delay_input.text())
            if self.sweep_class() == "ArraySweep":
                points = len(evaluate_array_expression(self.array_input.text()))
            else:
                points = self.num_input.value()
        except ValueError:
            return None
        return points, delay

    # ----- building the sweep -----
    @staticmethod
    def _float(text, what):
        try:
            return float(text)
        except ValueError:
            raise ValueError(f"{what} must be a number.") from None

    def _delay(self):
        return self._float(self.delay_input.text(), "The delay")

    def get_sweep(self, post_action=None, make_action=None):
        """Build the QCoDeS sweep from the fields. Raises ValueError with a readable message.

        ``post_action`` (optional callable) is run by dond after each point of this sweep, then the actions of the
        axis: ``make_action(action)`` turns each enabled one into a callable (it raises ValueError on a syntax error).
        """
        actions = (post_action,) if post_action else ()
        if make_action is not None:
            actions += tuple(make_action(a) for a in self.actions if a.get("enabled", True))
        sweep_class = self.sweep_class()
        if sweep_class == "TogetherSweep":
            return self._together_sweep(actions)
        parameter = self.component_selector.parameter()
        if parameter is None:
            raise ValueError("Select a sweep component first.")
        if sweep_class == "ArraySweep":
            return ArraySweep(parameter, evaluate_array_expression(self.array_input.text()), self._delay(),
                              post_actions=actions, get_after_set=self.get_after_set)
        start = self._float(self.start_input.text(), "Start")
        stop = self._float(self.stop_input.text(), "Stop")
        num_points, delay = self.num_input.value(), self._delay()
        if sweep_class == "LogSweep":
            # QCoDeS' LogSweep takes base-10 exponents; the fields hold the actual values
            if start <= 0 or stop <= 0:
                raise ValueError("A LogSweep needs Start and Stop above 0.")
            return LogSweep(parameter, np.log10(start), np.log10(stop), num_points, delay, post_actions=actions,
                            get_after_set=self.get_after_set)
        return LinSweep(parameter, start, stop, num_points, delay, post_actions=actions, get_after_set=self.get_after_set)

    def _together_sweep(self, actions=()):
        parameters = [selector.parameter() for selector in self.together_selectors]
        if any(p is None for p in parameters):
            raise ValueError("Select the components of both Sweep 1 and Sweep 2.")
        if parameters[0] is parameters[1]:
            raise ValueError("Sweep 1 and Sweep 2 must be different parameters.")
        num_points, delay = self.num_input.value(), self._delay()
        sweeps = []
        for n, parameter in enumerate(parameters):
            start = self._float(self.together_starts[n].text(), f"Start{n + 1}")
            stop = self._float(self.together_stops[n].text(), f"Stop{n + 1}")
            # the post action is attached once (to the first sweep): one call per together-step
            sweeps.append(LinSweep(parameter, start, stop, num_points, delay,
                                   post_actions=actions if n == 0 else (), get_after_set=self.get_after_set))
        return TogetherSweep(*sweeps)
