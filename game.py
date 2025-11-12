# game.py
from PySide6.QtWidgets import QWidget, QPushButton, QLabel

class GamePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Add your game content here
        label = QLabel("Game Screen", self)
        label.setStyleSheet("font-size: 24px; color: white;")
        label.setGeometry(100, 100, 300, 50)

        # Back button
        btn_back = QPushButton("POWRÓT DO MENU", self)
        btn_back.setGeometry(100, 200, 150, 40)
        btn_back.clicked.connect(self.main_window.show_menu)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: darkorange;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: orange;
            }
        """)
