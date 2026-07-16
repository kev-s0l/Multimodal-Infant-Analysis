from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QMainWindow,
    QSpinBox,
    QTabWidget,
    QWidget,
)

from app.controllers.language_controller import render_language_plot, run_language_analysis
from app.controllers.movement_controller import METRICS, render_movement_plot, run_movement_analysis
from app.controllers.multimodal_controller import render_multimodal_plot, run_multimodal_analysis
from app.controllers.sleep_controller import render_sleep_plot, run_sleep_analysis
from app.widgets.analysis_panel import AnalysisPanel
from app.widgets.file_picker import FilePicker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multimodal Infant Analysis")
        self.resize(1280, 780)

        tabs = QTabWidget()
        tabs.addTab(self._build_language_tab(), "Language")
        tabs.addTab(self._build_movement_tab(), "Movement")
        tabs.addTab(self._build_sleep_tab(), "Sleep")
        tabs.addTab(self._build_multimodal_tab(), "Multimodal")

        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Ready")

    def _build_language_tab(self) -> AnalysisPanel:
        its_picker = FilePicker("Select ITS file", "ITS files (*.its);;All files (*)")
        form = QFormLayout()
        form.addRow("ITS file", its_picker)
        widget = QWidget()
        widget.setLayout(form)

        return AnalysisPanel(
            "Language Analysis",
            widget,
            lambda: {"its_path": its_picker.path()},
            run_language_analysis,
            render_language_plot,
        )

    def _build_movement_tab(self) -> AnalysisPanel:
        h5_picker = FilePicker("Select H5 movement file", "H5 files (*.h5 *.hdf5);;All files (*)")
        sensor_id = QLineEdit()
        sensor_id.setPlaceholderText("Sensor ID inside Sensors group")

        metric = QComboBox()
        metric.addItems(METRICS)

        step = QSpinBox()
        step.setRange(1, 1_000_000)
        step.setValue(500)
        step.setToolTip("Used only for the Raw Acceleration plot/table.")

        form = QFormLayout()
        form.addRow("H5 file", h5_picker)
        form.addRow("Sensor ID", sensor_id)
        form.addRow("Metric", metric)
        form.addRow("Raw plot step", step)

        widget = QWidget()
        widget.setLayout(form)

        return AnalysisPanel(
            "Movement Analysis",
            widget,
            lambda: {
                "h5_path": h5_picker.path(),
                "sensor_id": sensor_id.text(),
                "metric": metric.currentText(),
                "step": step.value(),
            },
            run_movement_analysis,
            render_movement_plot,
        )

    def _build_sleep_tab(self) -> AnalysisPanel:
        mode = QComboBox()
        mode.addItems(["Text Sleep Profile", "EDF Fallback"])

        sleep_picker = FilePicker("Select sleep profile text file", "Text files (*.txt);;All files (*)")
        edf_picker = FilePicker("Select EDF file", "EDF files (*.edf);;All files (*)")

        eeg = QLineEdit("C4:M1")
        eog = QLineEdit("E1:M2")
        emg = QLineEdit("EMG1")
        use_movement = QCheckBox("Relabel low-confidence wake epochs as movement")

        form = QFormLayout()
        form.addRow("Mode", mode)
        form.addRow("Sleep profile", sleep_picker)
        form.addRow("EDF file", edf_picker)
        form.addRow("EEG channel", eeg)
        form.addRow("EOG channel", eog)
        form.addRow("EMG channel", emg)
        form.addRow("", use_movement)

        widget = QWidget()
        widget.setLayout(form)

        return AnalysisPanel(
            "Sleep Analysis",
            widget,
            lambda: {
                "mode": mode.currentText(),
                "sleep_path": sleep_picker.path(),
                "edf_path": edf_picker.path(),
                "eeg": eeg.text(),
                "eog": eog.text(),
                "emg": emg.text(),
                "use_movement": use_movement.isChecked(),
            },
            run_sleep_analysis,
            render_sleep_plot,
        )

    def _build_multimodal_tab(self) -> AnalysisPanel:
        mode = QComboBox()
        mode.addItems(["CoV + Sleep", "Pairwise CoV Comparison"])

        h5_picker = FilePicker("Select H5 movement file", "H5 files (*.h5 *.hdf5);;All files (*)")
        sleep_picker = FilePicker("Select sleep profile text file", "Text files (*.txt);;All files (*)")
        manifest_picker = FilePicker("Select manifest CSV", "CSV files (*.csv);;All files (*)")
        sensor_id = QLineEdit()
        sensor_id.setPlaceholderText("Sensor ID")

        form = QFormLayout()
        form.addRow("Mode", mode)
        form.addRow("H5 file", h5_picker)
        form.addRow("Sleep profile", sleep_picker)
        form.addRow("Sensor ID", sensor_id)
        form.addRow("Manifest CSV", manifest_picker)

        widget = QWidget()
        widget.setLayout(form)

        return AnalysisPanel(
            "Multimodal Analysis",
            widget,
            lambda: {
                "mode": mode.currentText(),
                "h5_path": h5_picker.path(),
                "sleep_path": sleep_picker.path(),
                "sensor_id": sensor_id.text(),
                "manifest_path": manifest_picker.path(),
            },
            run_multimodal_analysis,
            render_multimodal_plot,
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
