# game-settings.py

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QGroupBox, QSlider
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        screen_width = 1366 
        screen_height = 768
        
        self.setGeometry(30, 50, screen_width, screen_height)
        self.setFixedSize(screen_width, screen_height)
        self.main_window = main_window
        
        # --- Obraz tła ---
        self.background = QLabel(self)
        self.background.setGeometry(0,0, self.width(), self.height())
        pixmap = QPixmap("images/options/las.png")
        self.background.setScaledContents(True)  
        self.background.setPixmap(pixmap)
        self.background.lower()  
        
         # --- przezroczysty box ---
        self.sliders_panel = QGroupBox(self)
        self.sliders_panel.setStyleSheet("""
            QGroupBox {
                background-color: rgba(36, 41, 65, 180);
                border: 7px solid rgba(240, 178, 39, 200);
                border-radius: 15px;
            }
        """)
        
        panel_width = 900
        panel_height = 600
        x = (screen_width - panel_width) // 2
        y = (screen_height - panel_height) // 2
        self.sliders_panel.setGeometry(x, y, panel_width, panel_height)
        
        # --- title ---
        title_img = QLabel(self)
        title_img.setGeometry((screen_width-270)//2, 50, 270, 62)
        pixmap = QPixmap("images/buttons/settings-button.png")
        scaled_pixmap = pixmap.scaled(title_img.width(), title_img.height())
        title_img.setPixmap(scaled_pixmap)
        
         # --- współrzędne dla sliderów ---
        slider_x_start = 600
        slider_y_start = 150
        slider_width = 270
        slider_height = 62
        slider_padding = 15
        
        # --- music slider ---
        self.music_label = QLabel(self)
        self.music_label.setGeometry(350, 160, 160, 43)
        pixmap = QPixmap("images/options/music.png")
        scaled_pixmap = pixmap.scaled(self.music_label.width(), self.music_label.height())
        self.music_label.setPixmap(scaled_pixmap)
    
        self.music_slider = QSlider(Qt.Horizontal, self)
        self.music_slider.setGeometry(slider_x_start, slider_y_start, slider_width, slider_height)
        self.music_slider.setMinimum(0)
        self.music_slider.setMaximum(100)
        self.music_slider.setValue(80)
        self.music_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #555;
                height: 20px;
                width: 250px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: darkpurple;
                width: 25px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: rgba(240, 178, 39, 200);
            }
        """)
        
        self.music_value_label = QLabel("80%", self)
        self.music_value_label.setStyleSheet("font-size: 24px; color: rgba(240, 178, 39, 200);")
        self.music_value_label.setGeometry(950, 165, 70, 30)
        self.music_slider.valueChanged.connect(lambda v: self.music_value_label.setText(f"{v}%"))
        
        # Back button
        btn_back = QPushButton(self)
        btn_back.setGeometry((screen_width-215)//2, 600, 215, 43)
        btn_back.clicked.connect(self.main_window.show_menu)
        btn_back.setStyleSheet("""
            QPushButton {
                background-image: url(images/options/back_to_menu.png);
                background-position: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: orange;
            }
        """)
        
def get_music_volume(self):
    """Get music volume value (0-100)"""
    return self.music_slider.value()