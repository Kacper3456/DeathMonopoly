from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QStackedWidget
from PySide6.QtGui import QPixmap
from menu import MenuPage
from game import GamePage
from settings import SettingsPage
import sys

#Okno gry
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Game")
        self.setGeometry(30, 50, 1366, 768)
        self.setFixedSize(1366, 768)

        # --- tworzenie stosu ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- tworzenie stron ---
        self.menu_page = MenuPage(self)
        self.game_page = GamePage(self)
        self.settings_page = SettingsPage(self)

        # --- dodajemy strony do stosu ---
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.game_page)
        self.stacked_widget.addWidget(self.settings_page)

        # --- zaleności ---
        self.menu_page.main_window = self
        self.game_page.main_window = self
        self.settings_page.main_window = self

        self.show_menu()

    def keyPressEvent(self, event):
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_Escape:
            self.show_menu()
        else:
            super().keyPressEvent(event)

    def show_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_page)

    def show_game(self):
        self.stacked_widget.setCurrentWidget(self.game_page)

    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

#włączanie aplikacji
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
