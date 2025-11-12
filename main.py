from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap
from menu import MainWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()