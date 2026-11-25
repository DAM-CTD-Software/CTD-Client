from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class Measurements(QWidget):
    def __init__(self, bottle_count: int = 13):
        super().__init__()
        layout = QVBoxLayout(self)
        content = QHBoxLayout()
        layout.addLayout(content, 1)
        left = QVBoxLayout()
        content.addLayout(left, 3)

        self.alerts = Alerts(self)
        self.dship = Dship(self)
        self.bottle_depths = BottleDepths(bottle_count)
        left.addWidget(self.alerts)
        left.addWidget(self.dship)
        content.addWidget(self.bottle_depths, 2)

        self.measurement_group = QGroupBox("Measurement", self)
        controls = QGridLayout(self.measurement_group)
        left.addWidget(self.measurement_group)
        left.addStretch()

        self.current_filename = QLabel("--")
        self.last_filename = QLabel("--")
        controls.addWidget(QLabel("Current file"), 0, 0)
        controls.addWidget(self.current_filename, 0, 1)
        controls.addWidget(QLabel("Last file name"), 1, 0)
        controls.addWidget(self.last_filename, 1, 1)

        self.cast_number = QSpinBox()
        self.cast_number.setRange(1, 999999)
        controls.addWidget(QLabel("Cast number"), 2, 0)
        controls.addWidget(self.cast_number, 2, 1)

        self.operator = QComboBox()
        self.operator.setEditable(True)
        controls.addWidget(QLabel("Operator"), 3, 0)
        controls.addWidget(self.operator, 3, 1)

        self.station_override = QLineEdit()
        controls.addWidget(QLabel("Override position alias"), 4, 0)
        controls.addWidget(self.station_override, 4, 1)
        controls.setColumnStretch(1, 1)

        self.stopwatch = Stopwatch(self)
        stopwatch = QHBoxLayout()
        stopwatch.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stopwatch.addWidget(self.stopwatch)
        stopwatch.addStretch()
        layout.addLayout(stopwatch)

        self.autostart = QCheckBox("Autostart")
        self.autostart.setChecked(True)
        options = QHBoxLayout()
        options.addWidget(self.autostart)
        options.addStretch()
        layout.addLayout(options)

        self.measurement_button = QPushButton("Start Seasave")
        self.processing_button = QPushButton("Run Processing")
        self.measurement_button.setEnabled(False)
        self.processing_button.setEnabled(False)
        actions = QHBoxLayout()
        actions.addWidget(self.measurement_button)
        actions.addStretch()
        actions.addWidget(self.processing_button)
        layout.addLayout(actions)


class Alerts(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Alerts", parent)
        layout = QVBoxLayout(self)
        self.alerts_label = QLabel("No alerts")
        layout.addWidget(self.alerts_label)


class Stopwatch(QPushButton):
    def __init__(self, parent=None):
        super().__init__("00:00:00", parent)
        self.setMinimumSize(220, 70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to reset stopwatch")
        self.setAccessibleName("Stopwatch: click to reset")

        self._elapsed = QElapsedTimer()
        self._elapsed.start()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_time)
        self._timer.start(250)
        self.clicked.connect(self.reset)

    def reset(self):
        self._elapsed.restart()
        self.update_time()

    def update_time(self):
        hours, remainder = divmod(self._elapsed.elapsed() // 1000, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.setText(f"{hours:02}:{minutes:02}:{seconds:02}")


class Dship(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("DSHIP", parent)
        layout = QFormLayout(self)
        self.status = QLabel("Not connected")
        layout.addRow("Status", self.status)

        fields = {
            "Station": "Station",
            "GPS_Time": "GPS time",
            "GPS_Lat": "GPS latitude",
            "GPS_Lon": "GPS longitude",
            "Water_Depth": "Water depth (m)",
            "Air_Pressure": "Air pressure (hPa)",
            "Pos_Alias": "Position alias",
        }
        self.value_labels = {}
        for key, name in fields.items():
            label = QLabel("--")
            self.value_labels[key] = label
            layout.addRow(name, label)


class BottleDepths(QGroupBox):
    def __init__(self, bottle_count: int):
        super().__init__("Bottle depths (m)")
        layout = QVBoxLayout(self)
        self.table = QTableWidget(bottle_count, 2)
        self.table.setHorizontalHeaderLabels(["Bottle", "Depth (m)"])
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.CurrentChanged
        )
        self.table.setStyleSheet("""
    QLineEdit {
        qproperty-alignment: AlignCenter;
    }
""")

        for row in range(bottle_count):
            bottle = QTableWidgetItem(f"{row + 1}")
            bottle.setFlags(Qt.ItemFlag.NoItemFlags)
            bottle.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, bottle)
            empty_entry = QTableWidgetItem("")
            empty_entry.setFlags(
                Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )
            empty_entry.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, empty_entry)

        layout.addWidget(self.table)
