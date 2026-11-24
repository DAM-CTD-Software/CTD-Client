"""Processing settings and saved workflows edited with CTDAM's GUI."""

import tomllib
from pathlib import Path

import tomlkit
from ctdam.entry.gui import MainWindow as CtdamEditor
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class WorkflowEditor(CtdamEditor):
    workflow_changed = Signal(str)

    def load_toml(self, checked=False, file_path=None):
        previous_document = self.current_toml_document
        super().load_toml(checked=checked, file_path=file_path)
        if self.current_toml_document is not previous_document:
            self.workflow_changed.emit(str(self.current_toml_path))

    def save_toml(self, checked=False):
        previous_revision = file_revision(self.current_toml_path)
        super().save_toml(checked=checked)
        revision = file_revision(self.current_toml_path)
        if revision is not None and revision != previous_revision:
            self.workflow_changed.emit(str(revision[0]))


class WorkflowEntry(QGroupBox):
    def __init__(self, path):
        super().__init__()
        layout = QHBoxLayout(self)
        self.enabled = QCheckBox(path.name)
        self.enabled.setChecked(True)
        self.enabled.setAccessibleName(f"Enable workflow {path.name}")
        layout.addWidget(self.enabled, 1)
        self.edit_button = QPushButton("Edit")
        self.edit_button.setAccessibleName(f"Edit workflow {path.name}")
        layout.addWidget(self.edit_button)
        self.remove_button = QPushButton("Remove")
        self.remove_button.setAccessibleName(f"Remove workflow {path.name}")
        self.remove_button.setToolTip(
            "Remove from the list; keep the TOML file"
        )
        layout.addWidget(self.remove_button)


class Processing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflow_entries = {}
        layout = QVBoxLayout(self)

        settings_group = QGroupBox("General settings")
        settings = QVBoxLayout(settings_group)
        self.auto_process = QCheckBox(
            "Process automatically after a measurement"
        )
        settings.addWidget(self.auto_process)
        layout.addWidget(settings_group)

        workflows_group = QGroupBox("Workflows")
        workflows = QVBoxLayout(workflows_group)
        self.create_workflow_button = QPushButton(
            "Create new processing workflow"
        )
        self.create_workflow_button.clicked.connect(lambda: self.open_editor())
        workflows.addWidget(self.create_workflow_button)

        self.empty_state = QLabel("No workflows added yet.")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container = QWidget()
        self.workflow_layout = QVBoxLayout(container)
        self.workflow_layout.setContentsMargins(0, 0, 0, 0)
        self.workflow_layout.addWidget(self.empty_state)
        self.workflow_layout.addStretch()
        self.workflow_scroll = QScrollArea()
        self.workflow_scroll.setWidgetResizable(True)
        self.workflow_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.workflow_scroll.setWidget(container)
        workflows.addWidget(self.workflow_scroll, 1)
        layout.addWidget(workflows_group, 1)

    def add_workflow(self, file_path):
        path = Path(file_path).resolve()
        try:
            with path.open("rb") as file:
                document = tomllib.load(file)
            modules = document.get("modules", {})
            if not isinstance(modules, dict):
                raise ValueError("The modules setting must be a TOML table.")
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Cannot add workflow", str(error))
            return

        entry = self.workflow_entries.get(path)
        if entry is None:
            entry = WorkflowEntry(path)
            entry.edit_button.clicked.connect(lambda: self.open_editor(path))
            entry.remove_button.clicked.connect(
                lambda: self.remove_workflow(path)
            )
            self.workflow_entries[path] = entry
            ordered = sorted(
                self.workflow_entries, key=lambda path: path.name.casefold()
            )
            self.workflow_layout.insertWidget(ordered.index(path), entry)
        entry.setToolTip(f"{path}\n\nModules: {', '.join(modules) or 'None'}")
        self.empty_state.hide()

    def remove_workflow(self, path):
        entry = self.workflow_entries.pop(path)
        self.workflow_layout.removeWidget(entry)
        entry.hide()
        entry.deleteLater()
        self.empty_state.setVisible(not self.workflow_entries)

    def open_editor(self, file_path=None):
        editor = WorkflowEditor()
        editor.setParent(self, Qt.WindowType.Window)
        editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        editor.workflow_changed.connect(self.add_workflow)
        editor.current_toml_document = None
        if file_path is not None:
            editor.load_toml(file_path=file_path)
        else:
            editor.current_toml_path = Path("new_processing.toml")
            editor.current_toml_document = tomlkit.document()
            editor.current_toml_document["modules"] = tomlkit.table()
            editor.toml_panel.toml_title.setText("New processing workflow")
            editor.toml_panel.show_toml_modules(editor.current_toml_document)
        editor.showMaximized()


def file_revision(file_path):
    if file_path is None:
        return None
    try:
        path = Path(file_path).resolve()
        stat = path.stat()
        return path, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size
    except OSError:
        return None
