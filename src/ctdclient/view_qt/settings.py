from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        processing = QGroupBox("Processing settings")
        processing_layout = QVBoxLayout(processing)
        self.auto_process = QCheckBox(
            "Process automatically after every measurments"
        )
        processing_layout.addWidget(self.auto_process)
        layout.addWidget(processing)

        measurement = QGroupBox("Measurement settings")
        layout.addWidget(measurement)

        layout.addStretch()
