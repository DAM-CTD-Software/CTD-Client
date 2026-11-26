from ctdam.entry.gui import MainWindow as ModuleEditor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class Processing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        load_workflow_btn = QPushButton(self)
        load_workflow_btn.setText("Load an existing Workflow")
        new_workflow_btn = QPushButton(self)
        new_workflow_btn.setText("Create a new Workflow")
        new_workflow_btn.clicked.connect(lambda: new_workflow())
        scrollable_area = QScrollArea()
        scrollable_area.setWidgetResizable(True)
        container = QWidget()
        entries = QVBoxLayout(container)
        entries.setAlignment(Qt.AlignmentFlag.AlignTop)

        scrollable_area.setWidget(container)

        layout.addWidget(load_workflow_btn)
        layout.addWidget(new_workflow_btn)
        layout.addWidget(scrollable_area)

        displayed_workflow_paths = (
            set()
        )  # only unique paths to avoid duplications

        def new_workflow():
            editor = ModuleEditor()
            editor.setParent(self, Qt.WindowType.Window)
            editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            editor.workflow_saved.connect(
                add_workflow
            )  # uses the signal from ctdam to know when to add the entry
            editor.resize(1000, 1000)
            editor.show()

        def add_workflow(path):
            path = path.resolve()
            if path not in displayed_workflow_paths:
                entries.addWidget(WorkflowEntry(path.name))
                displayed_workflow_paths.add(path)


class WorkflowEntry(QGroupBox):
    "Represents an Entry of a proccessing workflow"

    def __init__(self, name: str, parent=None):
        super().__init__(parent)

        self.enabled = QCheckBox(name)
        self.edit_button = QPushButton("Edit")
        self.remove_button = QPushButton("Remove")

        layout = QHBoxLayout(self)
        layout.addWidget(self.enabled, 1)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.remove_button)
