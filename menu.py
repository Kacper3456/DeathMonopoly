from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, 
                             QGroupBox)
from PySide6.QtGui import QPixmap
import sys

class MenuPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # --- współrzędne dla przycisków ---
        buttons_x_start = 500
        buttons_y_start = 390
        button_width = 270
        button_height = 62
        button_padding = 15
        
        #jeden styl dla wszystkich przycisków
        def apply_button_style(button, image_path):
            button.setStyleSheet(f"""
                QPushButton {{
                    background-image: url({image_path});
                    background-position: center;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 215, 0, 0.7);
                }}
                QPushButton:pressed {{
                    background-color: orange;
                }}
            """)
        
        # --- Obraz tła ---
        self.background = QLabel(self)
        self.background.setGeometry(0,0, self.width(), self.height())
        pixmap = QPixmap("images/stars.png")
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
        pixmap = QPixmap("images/logo.jpg")
        scaled_pixmap = pixmap.scaled(logo_img.width(), logo_img.height())
        logo_img.setPixmap(scaled_pixmap)
        
        # --- Przycisk START ---
        btn_start = QPushButton(self.menu_box)
        btn_start.setGeometry(buttons_x_start, buttons_y_start, button_width, button_height)

        btn_start.clicked.connect(self.main_window.show_game)
        apply_button_style(btn_start, "images/buttons/start-button.png")
        
        # --- Przycisk USTAWIENIA ---
        btn_settings = QPushButton(self.menu_box)
        btn_settings.setGeometry(buttons_x_start, buttons_y_start + button_height + button_padding, button_width, button_height)
        btn_settings.clicked.connect(self.main_window.show_settings)
        apply_button_style(btn_settings, "images/buttons/settings-button.png")
        
        # --- Przycisk WYJŚCIE ---
        btn_exit = QPushButton(self.menu_box)
        btn_exit.setGeometry(buttons_x_start, buttons_y_start + 2 * button_height + 2 * button_padding, button_width, button_height)
        btn_exit.clicked.connect(QApplication.instance().quit)
        apply_button_style(btn_exit, "images/buttons/quit-button.png")
        
        
    def resizeEvent(self, event):
        self.background.resize(self.size())
        