from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        measurement_settings = Measurement()
        proccessing_settings = Proccessing()

        layout.addWidget(measurement_settings)
        layout.addWidget(proccessing_settings)
        layout.addStretch()


class Measurement(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Measurement settings", parent)
        layout = QGridLayout(self)

        self.cast_number_label = QLabel("Cast Number")
        self.cast_number = QSpinBox()
        self.cast_number.setRange(1, 999999)

        self.override_pos_alias_label = QLabel("Override position alias")
        self.pos_alias_override = QLineEdit()

        self.bottles_label = QLabel("Set Bottles count")
        self.bottles_edit = QLineEdit()

        layout.addWidget(self.cast_number_label, 0, 0)
        layout.addWidget(self.cast_number, 0, 1)
        layout.addWidget(self.override_pos_alias_label, 1, 0)
        layout.addWidget(self.pos_alias_override, 1, 1)
        layout.addWidget(self.bottles_label, 2, 0)
        layout.addWidget(self.bottles_edit, 2, 1)


class Proccessing(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Proccessing settings", parent)
        layout = QGridLayout(self)
        self.auto_process = QCheckBox(
            "Process automatically after every measurments"
        )
        layout.addWidget(self.auto_process)
