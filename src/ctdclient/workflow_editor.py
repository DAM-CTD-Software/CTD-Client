import sys

from ctdam.entry.gui import MainWindow
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.load_toml(file_path=sys.argv[1])
    window.showMaximized()
    app.exec()


if __name__ == "__main__":
    main()
