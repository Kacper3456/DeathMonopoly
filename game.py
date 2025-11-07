# game.py
from PySide6.QtWidgets import QWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap
from menu import MenuWindow  # importujemy, by móc wrócić

class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Okno Gry")
        self.setGeometry(300, 200, 600, 400)

        # --- Tło gry ---
        self.background = QLabel(self)
        pixmap = QPixmap("program_files/game_background.jpg")
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.resize(self.size())

        # --- Przycisk powrotu do menu ---
        self.btn_back = QPushButton("WRÓĆ DO MENU", self)
        self.btn_back.setGeometry(230, 300, 150, 40)
        self.btn_back.clicked.connect(self.back_to_menu)

    def resizeEvent(self, event):
        self.background.resize(self.size())

    def back_to_menu(self):
        # Wracamy do menu
        self.menu = MenuWindow()
        self.menu.show()
        self.close()
