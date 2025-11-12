# game.py
from PySide6.QtWidgets import QWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap
from menu import MenuWindow  # importujemy, by móc wrócić

class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Okno Gry")
        
        # Add your game content here
        label = QLabel("Game Screen", self)
        label.setStyleSheet("font-size: 24px; color: white;")
        label.setGeometry(100, 100, 300, 50)

        # --- Tło gry ---
        self.background = QLabel(self)
        pixmap = QPixmap("program_files/game_background.jpg")
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.resize(self.size())

        # --- Przycisk powrotu do menu ---
        btn_back = QPushButton("WRÓĆ DO MENU", self)
        btn_back.setGeometry(230, 300, 150, 40)
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

    def resizeEvent(self, event):
        self.background.resize(self.size())

    def back_to_menu(self):
        # Wracamy do menu
        self.menu = MenuWindow()
        self.menu.show()
        self.close()
