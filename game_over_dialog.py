from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class GameOverDialog(QDialog):
    """Wyświetla okno Game Over i resetuje grę"""
    def __init__(self, parent, player_name, final_balance):
        super().__init__(parent)
        

        self.setWindowTitle("Game Over")
        self.setStyleSheet("background-color: rgb(38, 39, 59);")
        self.setFixedSize(500, 350)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Tekst ---
        text = QLabel()
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setFont(QFont("Helvetica", 18))
        text.setStyleSheet("color: white; padding: 10px;")
        text.setText(
            f"""
            <b style='color: rgb(255, 50, 50); font-size: 32px;'>GAME OVER</b><br><br>
            <span style='color: rgb(255, 215, 0); font-size: 24px;'>Congratulations, {player_name}!</span><br><br>
            <span style='color: white; font-size: 20px;'>Final Balance: ${final_balance}</span><br><br>
            <span style='color: white; font-size: 16px;'>What would you like to do?</span>
            """
        )
        layout.addWidget(text)

        # --- Przyciski ---
        btn_layout = QHBoxLayout()
        button_width = 170
        button_height = 30

        btn_menu = QPushButton()
        btn_restart = QPushButton()

        def style_btn(btn, img):
            btn.setFixedSize(button_width, button_height)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-image: url({img});
                    background-position: center;
                    background-repeat: no-repeat;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 215, 0, 0.5);
                }}
                QPushButton:pressed {{
                    background-color: orange;
                }}
            """)

        style_btn(btn_menu, "images/buttons/return-to-menu.png")
        style_btn(btn_restart, "images/buttons/play-again.png")

        btn_layout.addWidget(btn_menu)
        btn_layout.addWidget(btn_restart)
        layout.addLayout(btn_layout)

        btn_menu.clicked.connect(self.accept)   # powrót do menu
        btn_restart.clicked.connect(self.reject)  # restart gry
