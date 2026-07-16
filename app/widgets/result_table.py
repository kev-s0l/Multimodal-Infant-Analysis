from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


class ResultTable(QTableWidget):
    def show_dataframe(self, df: pd.DataFrame, max_rows: int = 500) -> None:
        frame = df.copy()
        if frame.index.name is not None or not isinstance(frame.index, pd.RangeIndex):
            frame = frame.reset_index()
        frame = frame.head(max_rows)

        self.clear()
        self.setRowCount(len(frame))
        self.setColumnCount(len(frame.columns))
        self.setHorizontalHeaderLabels([str(col) for col in frame.columns])

        for row_idx, (_, row) in enumerate(frame.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem("" if pd.isna(value) else str(value))
                self.setItem(row_idx, col_idx, item)

        self.resizeColumnsToContents()

    def clear_results(self) -> None:
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)
