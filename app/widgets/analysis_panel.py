from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.widgets.plot_canvas import PlotCanvas
from app.widgets.result_table import ResultTable


class AnalysisWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, work: Callable[[], dict], parent=None):
        super().__init__(parent)
        self.work = work

    def run(self) -> None:
        try:
            self.completed.emit(self.work())
        except Exception as exc:
            self.failed.emit(str(exc))


class AnalysisPanel(QWidget):
    def __init__(
        self,
        title: str,
        input_widget: QWidget,
        collect_inputs: Callable[[], dict],
        run_analysis: Callable[[dict], dict],
        render_plot: Callable[[PlotCanvas, dict], None] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self.collect_inputs = collect_inputs
        self.run_analysis = run_analysis
        self.render_plot = render_plot
        self.worker: AnalysisWorker | None = None
        self.results: dict | None = None

        self.run_button = QPushButton("Run Analysis")
        self.run_button.clicked.connect(self._start)

        self.status = QLabel("Ready")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.table_selector = QComboBox()
        self.table_selector.currentIndexChanged.connect(self._show_selected_table)
        self.table = ResultTable()

        self.figure_selector = QComboBox()
        self.figure_selector.currentIndexChanged.connect(self._show_selected_plot)
        self.canvas = PlotCanvas()

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.run_button)
        action_layout.addWidget(self.status, 1)

        controls = QVBoxLayout()
        controls.addWidget(QLabel(f"<b>{title}</b>"))
        controls.addWidget(input_widget)
        controls.addLayout(action_layout)

        tables_page = QWidget()
        tables_layout = QVBoxLayout(tables_page)
        tables_layout.addWidget(self.table_selector)
        tables_layout.addWidget(self.table)

        plots_page = QWidget()
        plots_layout = QVBoxLayout(plots_page)
        plots_layout.addWidget(self.figure_selector)
        plots_layout.addWidget(self.canvas)

        output_tabs = QTabWidget()
        output_tabs.addTab(tables_page, "Tables")
        output_tabs.addTab(plots_page, "Graphs")
        output_tabs.addTab(self.log, "Messages")

        splitter = QSplitter()
        left = QWidget()
        left.setLayout(controls)
        splitter.addWidget(left)
        splitter.addWidget(output_tabs)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

    def _start(self) -> None:
        self._set_busy(True)
        self.log.clear()
        self.table.clear_results()
        self.table_selector.clear()
        self.figure_selector.clear()
        self.canvas.figure.clear()
        self.canvas.draw_idle()

        params = self.collect_inputs()
        self.worker = AnalysisWorker(lambda: self.run_analysis(params), self)
        self.worker.completed.connect(self._complete)
        self.worker.failed.connect(self._fail)
        self.worker.finished.connect(lambda: self._set_busy(False))
        self.worker.start()

    def _complete(self, result: dict) -> None:
        self.results = result
        self.log.setPlainText(result.get("message", "Analysis complete."))

        tables = result.get("tables", [])
        for table in tables:
            self.table_selector.addItem(table["title"])

        figures = result.get("figures", [])
        for figure in figures:
            self.figure_selector.addItem(figure["title"])

        self.status.setText("Complete")
        if tables:
            self._show_selected_table(0)
        if figures:
            self._show_selected_plot(0)

    def _fail(self, message: str) -> None:
        self.results = None
        self.status.setText("Error")
        self.log.setPlainText(message)

    def _show_selected_table(self, index: int) -> None:
        if not self.results or index < 0:
            return
        tables = self.results.get("tables", [])
        if index < len(tables):
            self.table.show_dataframe(tables[index]["data"])

    def _show_selected_plot(self, index: int) -> None:
        if not self.results or self.render_plot is None or index < 0:
            return
        figures = self.results.get("figures", [])
        if index < len(figures):
            self.render_plot(self.canvas, figures[index])

    def _set_busy(self, busy: bool) -> None:
        self.run_button.setEnabled(not busy)
        if busy:
            self.status.setText("Running...")
