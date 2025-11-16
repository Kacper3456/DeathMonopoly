from PySide6.QtWidgets import QWidget, QLabel, QGroupBox, QScrollArea, QMenu, QPushButton
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt, QPoint
from npc_manager import NPCManager
from player_manager import PlayerManager
from action_manager import ActionManager


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class GamePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # --- zarządzanie danymi gracza ---
        self.player_manager = PlayerManager()
        # --- zarządzanie opcjami akcyjnymi ---
        self.action_manager = ActionManager()


        # --- współrzędne dla Opcji akcyjnych ---
        action_x_start = self.action_manager.action_x_start
        action_y_start = self.action_manager.action_y_start

        # --- Tło gry ---
        self.background = QLabel(self)
        pixmap = QPixmap("images/stars.png")
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.resize(self.size())

        # --- Box do grupowania opcji aukcyjnych ---
        self.menu_box = QGroupBox(self)
        self.menu_box.setStyleSheet("QGroupBox { border: none; }")
        self.menu_box.setGeometry(0,0, 1100, 800)

         # --- Tworzenie opcji akcyjnych za pomocą ActionManager ---
        self.action_widgets = self.action_manager.create_action_widgets(self.menu_box)
        
        # Podłącz sygnały kliknięcia dla każdej akcji
        for action_widget in self.action_widgets:
            action_widget.clicked.connect(
                lambda checked=False, widget=action_widget: self.action_manager.show_action_menu(widget, self)
            )
        
        # --- Players Box ---
        self.playerBox = QLabel(self)
        self.playerBox.setGeometry(1100, action_y_start+60, 250, 370)
        self.playerBox.setStyleSheet("QLabel { background-color: rgba(38, 39, 59, 0.8); }")
        
        # --- Currency Box ---
        self.currencyBox = QLabel(self)
        self.currencyBox.setGeometry(1100, action_y_start, 250, 40)
        self.currencyBox.setStyleSheet("QLabel { background-color: rgba(38, 39, 59, 0.8); }")

        # --- Avatar Box ---
        self.avatarBox = QLabel(self)
        self.avatarBox.setGeometry(1100, 495, 250, 250)
        self.avatarBox.setStyleSheet("QLabel { background-color: rgba(38, 39, 59, 0.8); }")
        
         # --- Przycisk powrotu do gracza (Me) ---
        self.btn_player = QPushButton("ME", self)
        self.btn_player.setGeometry(1110, action_y_start+450, 40, 20)
        self.btn_player.setStyleSheet("""
            QPushButton {
                background-color: rgba(38, 39, 59, 0.8);
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid rgb(255, 215, 0);
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 215, 0, 1);
            }
            QPushButton:pressed {
                background-color: rgb(255, 165, 0);
            }
        """)
        self.btn_player.clicked.connect(self.show_player_character)
        self.btn_player.raise_() 
        
        self.avatar_image = QLabel(self.avatarBox)
        self.avatar_image.setAlignment(Qt.AlignCenter)
        self.avatar_image.setGeometry(0, 0, 250, 250)   
        pixmap = QPixmap("images/game_window/avatar/businessman.png")
        scaled_pixmap = pixmap.scaled(self.avatar_image.width(), self.avatar_image.height())
        self.avatar_image.setPixmap(scaled_pixmap)

        # --- Dialog Box (scrollable container) ---
        self.DialogBox = QScrollArea(self)
        self.DialogBox.setGeometry(action_x_start, 495, 1035, 250)
        self.DialogBox.setStyleSheet("""
            QScrollArea {
                background-color: rgba(38, 39, 59, 0.8);
                border: none;
            }
        """)
        self.DialogBox.setWidgetResizable(True)
        self.DialogBox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.DialogBox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # --- Dialog text ---
        self.dialogText = QLabel(self.DialogBox)
        self.dialogText.setWordWrap(True)
        self.dialogText.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.dialogText.setFont(QFont("Helvetica", 20))
        self.dialogText.setStyleSheet("color: white; padding: 10px; background-color: rgba(128, 0, 128, 0);")

        # Example long text
        self.dialogText.setText(
            "This is a long dialogue text that will scroll if it exceeds the visible area.\n\n"
            "You can add multiple paragraphs of dialogue here.\n\n"
            "Each line will wrap automatically, and the scrollbar will appear when needed.\n\n"
            + "Line\n" * 30
        )

        # Add text to box
        self.DialogBox.setWidget(self.dialogText)

        # --- Add scroll arrows ---
        self.upIndicator = QLabel("▲", self.DialogBox)
        self.upIndicator.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 8px;
            }
        """)
        self.upIndicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upIndicator.setFixedSize(30, 30)
        self.upIndicator.hide()

        self.downIndicator = QLabel("▼", self.DialogBox)
        self.downIndicator.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 8px;
            }
        """)
        self.downIndicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.downIndicator.setFixedSize(30, 30)
        self.downIndicator.hide()
        self.DialogBox.verticalScrollBar().valueChanged.connect(self.updateIndicators)
        self.updateIndicators()
        
        # --- NPC Manager - tutaj tworzymy i zarządzamy NPC ---
        self.npc_manager = NPCManager()
        self.npc_widgets = self.npc_manager.create_npc_widgets(self.playerBox)
        
        # Podłączamy aktualizację interfejsu po kliknięciu NPC
        for npc_widget in self.npc_widgets:
            npc_widget.clicked.connect(self.update_npc_display)
            
        # --- przycisk wyjście do menu ---
        btn_exit = QPushButton(self)
        btn_exit.setGeometry(1300, 15, 50, 32)
        btn_exit.clicked.connect(self.main_window.show_menu)
        btn_exit.setStyleSheet(f"""
                QPushButton {{
                    background-image: url("images/buttons/exit-button.png");
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

    # --- Update indicator visibility based on scroll position ---
    def updateIndicators(self):
        bar = self.DialogBox.verticalScrollBar()
        max_val = bar.maximum()
        val = bar.value()

        # position arrows inside the viewport
        w = self.DialogBox.viewport().width()
        h = self.DialogBox.viewport().height()

        self.upIndicator.move(w // 2 - 15, 5)
        self.downIndicator.move(w // 2 - 15, h - 35)

        # visibility logic
        self.upIndicator.setVisible(val > 0)
        self.downIndicator.setVisible(val < max_val)

    # --- Keep background scaling with window ---
    def resizeEvent(self, event):
        self.background.resize(self.size())
        self.updateIndicators()
        
    # --- pokazanie postaci gracza ---
    def show_player_character(self):
        
        self.player_data = self.player_manager.get_player_data()
        # --- Zmienić duzy awatar ---
        pixmap = QPixmap(self.player_data["avatar"])
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.avatar_image.width(), self.avatar_image.height(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.avatar_image.setPixmap(scaled_pixmap)
        
        #  --- Zmienić dialog --- 
        dialogue_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{self.player_data['name']}</b><br><br>{self.player_data['dialogue']}"
        self.dialogText.setText(dialogue_text)
        
        self.DialogBox.verticalScrollBar().setValue(0)
        
    def update_npc_display(self, index):
        
        npc_data = self.npc_manager.get_npc_data(index)
        if npc_data is None:
            return
        
        # --- Zmienić duzy awatar ---
        pixmap = QPixmap(npc_data["avatar"])
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.avatar_image.width(), self.avatar_image.height(),
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.avatar_image.setPixmap(scaled_pixmap)
        
        #  --- Zmienić dialog --- 
        dialogue_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{npc_data['name']}</b><br><br>{npc_data['dialogue']}"
        self.dialogText.setText(dialogue_text)
        
        # Scroll dialog na początek
        self.DialogBox.verticalScrollBar().setValue(0)

    def show_action_menu(self, target_label):
        """Deleguje pokazanie menu do ActionManager"""
        self.action_manager.show_action_menu(target_label, self)