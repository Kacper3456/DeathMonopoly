from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QStackedWidget
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt
from menu import MenuPage
from game import GamePage
from game_settings import SettingsPage
import sys

class BrightnessOverlay(QWidget):
    """A transparent overlay that darkens the whole window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.raise_()

    def setOpacity(self, opacity: float):
        """Set opacity between 0.0 (no dim) and 1.0 (completely black)."""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()

    def paintEvent(self, event):
        if self._opacity > 0:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, int(self._opacity * 255)))

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

        self.brightness_overlay = BrightnessOverlay(self)
        self.brightness_overlay.setGeometry(0, 0, self.width(), self.height())
        self.brightness_overlay.raise_()
        self.brightness_overlay.show()
        self.brightness_value = 50


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

    def set_brightness(self, value):
        """Set global brightness (0–100)."""
        self.brightness_value = value
        # Convert slider value (0–100) into overlay opacity (1.0 = dark)
        opacity = 1.0 - (value / 100.0)
        self.brightness_overlay.setOpacity(opacity)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "brightness_overlay"):
            self.brightness_overlay.resize(self.size())

#włączanie aplikacji
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
