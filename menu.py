from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGroupBox, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap
import sys

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.setGeometry(100, 100, 1366, 768)
        self.setFixedSize(1366, 768)

        # --- Obraz tła ---
        self.background = QLabel(self)
        self.setStyleSheet("background-color: purple;")

        # --- Menu Box ---
        self.menu_box = QGroupBox(self)
        self.menu_box.setStyleSheet("QGroupBox { border: none; }")
        self.menu_box.setGeometry(50, 30, 800, 800)

        # --- obraz menu ---
        menu_img = QLabel("START", self.menu_box)
        menu_img.setGeometry(50, 50, 300, 300)
        pixmap = QPixmap("program_files/menu_background.jpg")
        scaled_pixmap = pixmap.scaled(menu_img.width(), menu_img.height())
        menu_img.setPixmap(scaled_pixmap)

        # --- Przycisk START ---
        btn_start = QPushButton("START", self.menu_box)
        btn_start.setGeometry(150, 360, 120, 40)
        btn_start.clicked.connect(self.start_game, self.menu_box)
        btn_start.setStyleSheet("""
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
        btn_settings = QPushButton("USTAWIENIA", self.menu_box)
        btn_settings.setGeometry(150, 410, 120, 40)
        btn_settings.clicked.connect(self.open_settings)
        btn_settings.setStyleSheet("""
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
        btn_exit = QPushButton("WYJŚCIE", self.menu_box)
        btn_exit.setGeometry(150, 460, 120, 40)
        btn_exit.clicked.connect(self.close)
        btn_exit.setStyleSheet("""
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

