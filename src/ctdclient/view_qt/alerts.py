from PySide6.QtCore import Qt
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


class Alerts(QGroupBox):
    def __init__(self):
        super().__init__("Alerts")
        layout = QVBoxLayout(self)
        self.alerts_label = QLabel("No alerts")
        layout.addWidget(self.alerts_label)
