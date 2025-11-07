from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap
import sys

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.setGeometry(300, 200, 600, 400)

        # --- Obraz tła ---
        self.background = QLabel(self)
        pixmap = QPixmap("program_files/menu_background.jpg")
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.resize(self.size())

        # --- Przycisk START ---
        self.btn_start = QPushButton("START", self)
        self.btn_start.setGeometry(250, 150, 120, 40)
        self.btn_start.clicked.connect(self.start_game)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: darkorange;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: orange;
            }
            QPushButton:pressed {
                background-color: orange;
            }
        """)

        # --- Przycisk USTAWIENIA ---
        self.btn_settings = QPushButton("USTAWIENIA", self)
        self.btn_settings.setGeometry(250, 200, 120, 40)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: darkorange;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: orange;
            }
            QPushButton:pressed {
                background-color: orange;
            }
        """)

        # --- Przycisk WYJŚCIE ---
        self.btn_exit = QPushButton("WYJŚCIE", self)
        self.btn_exit.setGeometry(250, 250, 120, 40)
        self.btn_exit.clicked.connect(self.close)
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: darkorange;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: orange;
            }
            QPushButton:pressed {
                background-color: orange;
            }
        """)

    def resizeEvent(self, event):
        self.background.resize(self.size())

    def start_game(self):
            from game import GameWindow
            self.game_window = GameWindow()
            self.game_window.show()
            self.close()

    def open_settings(self):
        from settings import SettingsWindow
        self.game_window = SettingsWindow()
        self.game_window.show()
        self.close()

