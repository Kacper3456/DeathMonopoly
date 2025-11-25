# game-settings.py

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QGroupBox, QSlider, QRadioButton, QHBoxLayout, QButtonGroup
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        screen_width = 1366 
        screen_height = 768
        
        self.setFixedSize(screen_width, screen_height)
        self.main_window = main_window
        
        def keyPressEvent(self, event):
            w = self.focusWidget()
            # --- kierowanie slajderami ---    
            if isinstance(w, QSlider):
                if event.key() == Qt.Key_Right:
                    w.setValue(min(w.value() + 1, w.maximum()))
                return
            elif event.key() == Qt.Key_Left:
                w.setValue(max(w.value() - 1, w.minimum()))
                return
            # --- kierowanie radiobutton ---  
            if w == self.difficulty_container:
                if event.key() == Qt.Key_Right:
                    self._select_next_radio()
                    return
                if event.key() == Qt.Key_Left:
                    self._select_prev_radio()
                    return
                
            super().keyPressEvent(event)

        
        # ---------------- BACKGROUND ----------------
        self.background = QLabel(self)
        self.background.setGeometry(0,0, self.width(), self.height())
        pixmap = QPixmap("images/options/las.png")
        self.background.setScaledContents(True)  
        self.background.setPixmap(pixmap)
        self.background.lower()  
        
        # ---------------- MAIN PANEL ----------------
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
        
        # ---------------- TITLE ----------------
        title_img = QLabel(self)
        title_img.setGeometry((screen_width-270)//2, 50, 270, 62)
        pixmap = QPixmap("images/buttons/settings-button.png")
        scaled_pixmap = pixmap.scaled(title_img.width(), title_img.height())
        title_img.setPixmap(scaled_pixmap)
        
        # ---------------------------------------------------
        # ---------------- SLIDERY --------------------------
        # ---------------------------------------------------
        
        # --- współrzędne dla sliderów ---
        slider_x_start = 750
        slider_y_start = 150
        slider_width = 270
        slider_height = 62
        
        # --- współrzędne dla label ---
        label_x_start = 350
        label_y_start = 160
        label_height = 40
        margin = 70
        
        # --- MUSIC SLIDER ---
        self.music_label = QLabel(self)
        self.music_label.setGeometry(label_x_start, label_y_start, 160, label_height)
        pixmap = QPixmap("images/options/music.png")
        scaled_pixmap = pixmap.scaled(self.music_label.width(), self.music_label.height())
        self.music_label.setPixmap(scaled_pixmap)
    
        def apply_slider_style(slider):
            slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                background: #555;
                height: 20px;
                width: 250px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: darkpurple;
                width: 25px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: rgba(240, 178, 39, 200);
            }}
            QSlider:focus {{
                border: 2px solid rgba(240, 178, 39, 230);
            }}
            """)
            
        self.music_slider = QSlider(Qt.Horizontal, self)
        self.music_slider.setGeometry(slider_x_start, slider_y_start, slider_width, slider_height)
        self.music_slider.setMinimum(0)
        self.music_slider.setMaximum(100)
        self.music_slider.setValue(80)
        apply_slider_style(self.music_slider)
        self.music_slider.setFocusPolicy(Qt.StrongFocus)
        
        
        # zmieniający się procent głosności, ale mi się nie podoba czcionka
        # self.music_value_label = QLabel("80%", self)
        # self.music_value_label.setStyleSheet("font-size: 24px; color: rgba(240, 178, 39, 200);")
        # self.music_value_label.setGeometry(950, 165, 70, 30)
        # self.music_slider.valueChanged.connect(lambda v: self.music_value_label.setText(f"{v}%"))
        
        
        # --- BRIGHTNESS SLIDER ---
        self.brightness_label = QLabel(self)
        self.brightness_label.setGeometry(label_x_start, label_y_start+label_height+margin, 263, label_height)
        pixmap = QPixmap("images/options/brightness.png")
        scaled_pixmap = pixmap.scaled(self.brightness_label.width(), self.brightness_label.height())
        self.brightness_label.setPixmap(scaled_pixmap)
        
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setGeometry(slider_x_start, slider_y_start+110, slider_width, slider_height)
        self.brightness_slider.setMinimum(50)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.update_brightness)
        apply_slider_style(self.brightness_slider)
        self.brightness_slider.setFocusPolicy(Qt.StrongFocus)
        
        
        # --- DIFFICULTY LEVEL ---
        
        self.difficulty_label = QLabel(self)
        self.difficulty_label.setGeometry((screen_width-395)//2, label_y_start+2*label_height+2*margin, 400, label_height)
        pixmap = QPixmap("images/options/select_difficulty.png")
        scaled_pixmap = pixmap.scaled(self.difficulty_label.width(), self.difficulty_label.height())
        self.difficulty_label.setPixmap(scaled_pixmap)
        
        # --- container widget ---
        self.difficulty_container = QWidget(self)
        self.difficulty_container.setGeometry((screen_width-700)//2, 430, 700, 120)
        self.difficulty_container.setFocusPolicy(Qt.StrongFocus)

        
        # --- layout ---
        difficulty_layout = QHBoxLayout(self.difficulty_container)
        
        self.radio_easy = QRadioButton(self.difficulty_container)
        self.radio_medium = QRadioButton(self.difficulty_container)
        self.radio_hard = QRadioButton(self.difficulty_container)
        
        button_width = 180
        button_height = 60
        
        self.radio_easy.setFixedSize(button_width, button_height)
        self.radio_medium.setFixedSize(button_width, button_height)
        self.radio_hard.setFixedSize(button_width, button_height)

        def apply_radio_style(radio_button, image_path):
            radio_button.setStyleSheet(f"""
                QRadioButton {{
                    background-image: url({image_path});
                    background-position: center;
                    background-repeat: no-repeat;
                    border: none;
                    border-radius: 10px;
                }}
                QRadioButton:hover {{
                    background-color: rgba(255, 215, 0, 0.3);
                }}
                QRadioButton:checked {{
                    background-color: rgba(255, 215, 0, 0.5);
                    border: 3px solid #FFD700;
                }}
                QRadioButton::indicator {{
                    width: 0px;
                    height: 0px;
                }}
            """)
        
        apply_radio_style(self.radio_easy, "images/options/easy.png" )
        apply_radio_style(self.radio_medium, "images/options/medium.png" )
        apply_radio_style(self.radio_hard, "images/options/hard.png" )

        self.radio_easy.setChecked(True)
        
        difficulty_layout.addWidget(self.radio_easy)
        difficulty_layout.addWidget(self.radio_medium)
        difficulty_layout.addWidget(self.radio_hard)

        self.difficulty_group = QButtonGroup(self)
        self.difficulty_group.addButton(self.radio_easy, 1)   #id:1 
        self.difficulty_group.addButton(self.radio_medium, 2) 
        self.difficulty_group.addButton(self.radio_hard, 3)
        self.difficulty_group.buttonClicked.connect(self.on_difficulty_changed)


        # --- Back button ---
        btn_back = QPushButton(self)
        btn_back.setGeometry((screen_width-215)//2, 600, 215, 41)
        btn_back.clicked.connect(self.main_window.show_menu)
        btn_back.setStyleSheet("""
            QPushButton {
                background-image: url(images/options/back_to_menu.png);
                background-position: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 0.7);
            }
        """)
        btn_back.setFocusPolicy(Qt.StrongFocus)

        
    def get_music_volume(self):
        """Get music volume value (0-100)"""
        return self.music_slider.value()

    def get_difficulty_id(self):
        return self.difficulty_group.checkedId()  # zwróci 1, 2, or 3

    def on_difficulty_changed(self):
        difficulty = self.get_difficulty_id()
        self.main_window.game_page.init_balance(difficulty)
        
    def update_brightness(self, value):
            """Update main window brightness."""
            if hasattr(self.main_window, "set_brightness"):
                self.main_window.set_brightness(value)

    def disable_difficulty_buttons(self):
        self.radio_easy.blockSignals(True)
        self.radio_medium.blockSignals(True)
        self.radio_hard.blockSignals(True)

        self.radio_easy.setEnabled(False)
        self.radio_medium.setEnabled(False)
        self.radio_hard.setEnabled(False)

    def enable_difficulty_buttons(self):
        self.radio_easy.blockSignals(False)
        self.radio_medium.blockSignals(False)
        self.radio_hard.blockSignals(False)

        self.radio_easy.setEnabled(True)
        self.radio_medium.setEnabled(True)
        self.radio_hard.setEnabled(True)
        
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