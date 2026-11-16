"""Qt entry point for CTD-Client."""

import sys

from PySide6.QtWidgets import QApplication

from ctdclient import __version__
from ctdclient.view_qt.mainWindow import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("CTD-Client")
    app.setApplicationVersion(__version__)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
