from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget


class FilePicker(QWidget):
    def __init__(self, caption: str, file_filter: str, parent=None):
        super().__init__(parent)
        self.caption = caption
        self.file_filter = file_filter

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(caption)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit, 1)
        layout.addWidget(browse_button)

    def path(self) -> str:
        return self.line_edit.text().strip()

    def set_path(self, path: str) -> None:
        self.line_edit.setText(path)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.caption, "", self.file_filter)
        if path:
            self.line_edit.setText(path)
