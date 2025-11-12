from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, 
                             QGroupBox, QStackedWidget, QMainWindow)
from PySide6.QtGui import QPixmap, QIcon
import sys
from game import GamePage
from settings import SettingsPage

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


class MenuPage(QWidget):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        
        # --- Obraz tła ---
        self.background = QLabel(self)
        self.background.setGeometry(0,0, self.width(), self.height())
        pixmap = QPixmap("program_files/stars.png")
        self.background.setScaledContents(True)  
        self.background.setPixmap(pixmap)
        self.background.lower()  
        
        # --- Menu Box ---
        self.menu_box = QGroupBox(self)
        self.menu_box.setStyleSheet("QGroupBox { border: none; }")
        self.menu_box.setGeometry(50, 30, 800, 800)
        
        # --- obraz logo ---
        logo_img = QLabel("START", self.menu_box)
        logo_img.setGeometry(450, 50, 350, 300)
        pixmap = QPixmap("program_files/logo.jpg")
        scaled_pixmap = pixmap.scaled(logo_img.width(), logo_img.height())
        logo_img.setPixmap(scaled_pixmap)
        
        # --- Przycisk START ---
        btn_start = QPushButton(self.menu_box)
        btn_start.setGeometry(500, 390, 270, 62)

        btn_start.clicked.connect(self.main_window.show_game)
        btn_start.setStyleSheet("""
            QPushButton {
                background-image: url(images/buttons/start-button.png);
                background-position: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.7);
            }
        """)
        
        # --- Przycisk USTAWIENIA ---
        btn_settings = QPushButton(self.menu_box)
        btn_settings.setGeometry(500, 467, 270, 62)
        btn_settings.clicked.connect(self.main_window.show_settings)
        btn_settings.setStyleSheet("""
            QPushButton {
                background-image: url(images/buttons/settings-button.png);
                background-position: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.7);
            }
            QPushButton:pressed {
                background-color: orange;
            }
        """)
        
        # --- Przycisk WYJŚCIE ---
        btn_exit = QPushButton(self.menu_box)
        btn_exit.setGeometry(500, 544, 270, 62)
        btn_exit.clicked.connect(QApplication.instance().quit)
        btn_exit.setStyleSheet("""
            QPushButton {
                background-image: url(images/buttons/quit-button.png);
                background-position: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.7);
            }
            QPushButton:pressed {
                background-color: orange;
            }
        """)
        
    def resizeEvent(self, event):
        self.background.resize(self.size())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())