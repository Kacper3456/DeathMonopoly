from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QGuiApplication
from menu import MenuPage
from game import GamePage
from game_settings import SettingsPage, BrightnessOverlay
import sys
from stock_data import clear_stock_files


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # --- pobierz pełną rozdzielczość ekranu ---
        screen = QGuiApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        # --- pełny ekran ---
        self.showFullScreen()

        # --- stos stron ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # --- strony ---
        self.menu_page = MenuPage(self)
        self.game_page = GamePage(self)
        self.settings_page = SettingsPage(self)

        # --- dodanie stron ---
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.game_page)
        self.stacked_widget.addWidget(self.settings_page)

        # --- zależności ---
        self.menu_page.main_window = self
        self.game_page.main_window = self
        self.settings_page.main_window = self

        # --- start ---
        self.show_menu()

        # --- overlay jasności ---
        self.brightness_overlay = BrightnessOverlay(self)
        self.brightness_overlay.setGeometry(0, 0, self.width(), self.height())
        self.brightness_overlay.raise_()
        self.brightness_overlay.show()
        self.brightness_value = 50

    # --- klawisz ESC wraca do menu ---
    def keyPressEvent(self, event):
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_Escape:
            self.show_menu()
        else:
            super().keyPressEvent(event)

    # --- logika stron ---
    def show_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_page)

    def show_game(self):
        self.game_page.init_balance(self.settings_page.get_difficulty_id())
        self.stacked_widget.setCurrentWidget(self.game_page)

    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    # --- jasność ---
    def set_brightness(self, value):
        self.brightness_value = value
        opacity = 1.0 - (value / 100.0)
        self.brightness_overlay.setOpacity(opacity)

    # --- zmiana rozmiaru = zmiana overlay ---
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "brightness_overlay"):
            self.brightness_overlay.resize(self.size())

    # --- usuwa wygenerowane pliki podczas gry ---
    def closeEvent(self, event):
        clear_stock_files()  # delete CSV and chart files
        event.accept()


    # --- aplikacja ---
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # pełny ekran uruchamia się automatycznie
    app.exec()


if __name__ == "__main__":
    main()
