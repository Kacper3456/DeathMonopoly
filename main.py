from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap
from menu import MenuWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()