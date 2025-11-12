# game.py
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt

# store slider style
Slider_style ="""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: orange;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #222;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: darkorange;
                border: 1px solid #555;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: orange;
            }"""

class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Add your settings content here
        label = QLabel("Ustawienia", self)
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

        # Brightness slider
        self.brightnessSlider = QSlider(Qt.Horizontal, self)
        self.brightnessSlider.setGeometry(100, 260, 200, 30)
        self.brightnessSlider.setMinimum(50)
        self.brightnessSlider.setMaximum(100)
        self.brightnessSlider.setValue(100)
        self.brightnessSlider.setStyleSheet(Slider_style)
        self.brightnessSlider.valueChanged.connect(self.update_brightness)

        # Master sound slider
        self.masterSoundSlider = QSlider(Qt.Horizontal, self)
        self.masterSoundSlider.setGeometry(100, 280, 200, 30)  # directly under the button
        self.masterSoundSlider.setMinimum(0)
        self.masterSoundSlider.setMaximum(100)
        self.masterSoundSlider.setValue(100)
        self.masterSoundSlider.setStyleSheet(Slider_style)

        # Game sound slider
        self.gSoundSlider = QSlider(Qt.Horizontal, self)
        self.gSoundSlider.setGeometry(100, 300, 200, 30)  # directly under the button
        self.gSoundSlider.setMinimum(0)
        self.gSoundSlider.setMaximum(100)
        self.gSoundSlider.setValue(100)
        self.gSoundSlider.setStyleSheet(Slider_style)

        # Music sound slider
        self.mSoundSlider = QSlider(Qt.Horizontal, self)
        self.mSoundSlider.setGeometry(100, 320, 200, 30)  # directly under the button
        self.mSoundSlider.setMinimum(0)
        self.mSoundSlider.setMaximum(100)
        self.mSoundSlider.setValue(100)
        self.mSoundSlider.setStyleSheet(Slider_style)

    def update_brightness(self, value):
        """Update main window brightness."""
        if hasattr(self.main_window, "set_brightness"):
            self.main_window.set_brightness(value)