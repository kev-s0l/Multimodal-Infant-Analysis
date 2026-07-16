from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 5), tight_layout=True)
        super().__init__(self.figure)
        self.setParent(parent)

    def reset(self):
        self.figure.clear()
        return self.figure.add_subplot(111)
