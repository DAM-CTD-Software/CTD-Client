"""Main window for the Qt interface."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget

from ctdclient import __version__
from ctdclient.view_qt.measurements import Measurements


class MainWindow(QTabWidget):
    BASE_SIZE = QSize(700, 700)
    MIN_SCALE = 0.85
    MAX_SCALE = 1.5

    def __init__(self):
        super().__init__()
        self._base_font_size = self.font().pointSizeF()

        self.setWindowTitle(f"CTD Client {__version__}")
        self.tabBar().setAccessibleName("Pages")
        self.tabBar().setExpanding(True)

        self.measurements_window = Measurements()
        self.addTab(self.measurements_window, "Measurement")
        self.resize(self.BASE_SIZE)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        scale = min(
            self.width() / self.BASE_SIZE.width(),
            self.height() / self.BASE_SIZE.height(),
        )
        scale = max(self.MIN_SCALE, min(scale, self.MAX_SCALE))
        font_size = self._base_font_size * scale
        self.setStyleSheet(
            f"QWidget {{ font-size: {font_size}pt; }}"
            "QTableWidget, QHeaderView, QTableWidget QLineEdit "
            f"{{ font-size: {font_size * 1.25}pt; }}"
            "QTableWidget::item { padding: 6px; }"
        )
