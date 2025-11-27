from PySide6.QtWidgets import QWidget, QLabel, QGroupBox, QScrollArea, QPushButton, QMessageBox, QDialog, QVBoxLayout, \
    QApplication
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt
from game.npc_manager import NPCManager
from game.player_manager import PlayerManager
from game.action_manager import ActionManager
from game_over_dialog import GameOverDialog
from game.stock_data import get_data, get_data_chart, clear_stock_files


class LoadingDialog(QDialog):
    def __init__(self, message="Loading..."):
        super().__init__()
        self.setWindowTitle("Please wait")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)

        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # show busy cursor
        self.setCursor(Qt.BusyCursor)

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class GamePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.unspent_money = None

        # --- zarządzanie danymi gracza ---
        self.player_manager = PlayerManager()
        # --- zarządzanie opcjami akcyjnymi ---
        self.action_manager = ActionManager()

        # --- Licznik tur ---
        self.turn_counter = 0
        self.max_turns = 3

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


        def apply_button_style(button, image_path):
            button.setStyleSheet(f"""
                QPushButton {{
                    background-image: url({image_path});
                    background-position: center;
                    background-repeat: no-repeat;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 215, 0, 0.7);
                }}
                QPushButton:pressed {{
                    background-color: orange;
                }}
            """)

         # --- Przyciski Random i Start ---
        button_y = action_y_start + 2 * self.action_manager.action_height + 2 * self.action_manager.action_padding
        button_width = 136
        button_height = 33

        self.btn_random = QPushButton(self.menu_box)
        self.btn_random.setGeometry(400, button_y, button_width, button_height)
        self.btn_random.clicked.connect(self.randomize_actions)
        apply_button_style(self.btn_random, "images/buttons/random-button.png")

        self.btn_start = QPushButton(self.menu_box)
        self.btn_start.setGeometry(400 + button_width + 20, button_y, button_width, button_height)
        self.btn_start.clicked.connect(self.start_game)
        apply_button_style(self.btn_start, "images/buttons/start-button-small.png")

        # --- Przycisk Continue (ukryty na początku) ---
        self.btn_continue = QPushButton(self.menu_box)
        self.btn_continue.setGeometry(500, button_y, button_width, button_height)
        self.btn_continue.clicked.connect(self.continue_game)
        apply_button_style(self.btn_continue, "images/buttons/continue-button-small.png")
        self.btn_continue.hide()  # Ukryj na początku

        # Flaga czy gra się rozpoczęła
        self.game_started = False

        # --- Players Box ---
        self.playerBox = QLabel(self)
        self.playerBox.setGeometry(1100, action_y_start+60, 250, 370)
        self.playerBox.setStyleSheet("QLabel { background-color: rgba(38, 39, 59, 0.8); }")

        # --- Balance Box ---
        self.balanceBox = QLabel(self)
        self.balanceBox.setGeometry(1100, action_y_start, 250, 40)
        self.balanceBox.setStyleSheet("QLabel { background-color: rgba(38, 39, 59, 0.8); }")

        self.balance = QLabel(self.balanceBox)
        self.balance.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.balance.setFont(QFont("Comic Sans MS", 30))
        self.balance.setStyleSheet("color: green; padding: 0px; background-color: rgba(128, 0, 128, 0);")

        # Initialize label with current balance
        self.balance.setText(f"$ {self.player_manager.get_player_balance()}")

         # --- Tworzenie opcji akcyjnych za pomocą ActionManager ---
        self.action_widgets = self.action_manager.create_action_widgets(
            parent=self.menu_box,
            player_manager=self.player_manager,
            balance_label=self.balance
        )

        # Podłącz sygnały kliknięcia dla każdej akcji
        for action_widget in self.action_widgets:
            action_widget.image_label.clicked.connect(
                lambda checked=False, widget=action_widget: (
                    None if self.game_started else self.action_manager.show_action_menu(widget.image_label, self)
                )
            )

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

        # wstępny text
        self.dialogText.setText(
            "<b style='color: rgb(255, 215, 0); font-size: 24px;'>Welcome to the simulation for beginner investors.</b><br>"
            "It's time for your first market lesson.<br><br>"
            "<b style='color: rgb(255, 215, 0);'>Balance:</b><br>"
            "You can see your current balance at the top of the screen. You can change it in the settings (higher difficulty = less starting capital).<br><br>"
            "<b style='color: rgb(255, 215, 0);'>Selection:</b><br>"
            "You now need to choose 6 companies and specify how much money you will invest in them. Changes are possible later!<br><br>"
            "<b style='color: rgb(255, 215, 0);'>Advice:</b><br>"
            "On the right side, you will find My Friends. Listen to their advice, but remember – the decision is yours.<br><br>"
            "<b style='color: rgb(255, 215, 0);'>Goal:</b><br>"
            "You have 10 rounds. Try not to go bankrupt.<br><br>"
            "<b style='color: rgb(100, 255, 100); font-size: 36px;'>Good luck!!</b><br><br>"
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

    def init_balance(self, difficulty):
        if self.game_started:
            return

        if difficulty == 1:
            self.player_manager.set_player_balance(2400)
        elif difficulty == 2:
            self.player_manager.set_player_balance(1200)
        else:
            self.player_manager.set_player_balance(600)

        # Update balance display
        self.balance.setText(f"$ {self.player_manager.get_player_balance()}")

        # Reset all action value labels
        for widget in self.action_manager.action_widgets:
            widget.quantity = 0
            widget.value_label.setText("0")

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
        self.npc_manager.unselect_npc()

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
        self.action_manager.show_action_menu(target_label, self)

    def randomize_actions(self):
        """Losuje opcje dla wszystkich akcji"""
        self.action_manager.randomize_actions()

    def update_turn_display(self):
        """
        Shows a loading dialog, fetches stock data for the current turn,
        generates charts, and updates the action widgets with the new charts.
        """
        loading = LoadingDialog("Downloading stock data...\nThis may take a moment.")
        loading.show()
        QApplication.processEvents()

        # Get selected companies
        selected_companies = self.action_manager.get_selected_actions()
        turn = self.turn_counter

        # Generate data and charts
        get_data(selected_companies, turn)
        for company in selected_companies:
            get_data_chart(company)

        # Update the action widgets with new chart images
        self.action_manager.update_selected_action_charts()
        self.action_manager.update_value_labels_by_stock()

        #Update Balance
        total_value = sum(int(widget.value_label.text()) for widget in self.action_manager.action_widgets)
        new_balance = self.unspent_money + total_value
        self.player_manager.set_player_balance(new_balance)
        self.balance.setText(f"$ {new_balance}")

        # #Updating NPC Dialogue
        budget = self.player_manager.get_player_balance()
        for i, npc_widget in enumerate(self.npc_manager.npc_widgets):
            self.npc_manager.update_dialog_ai(i, player_balance=budget, selected_companies=selected_companies)

        loading.close()

    def start_game(self):
        if not self.action_manager.all_actions_selected():
            # Nie wszystkie akcje wybrane - pokaż komunikat
            missing = self.action_manager.get_missing_count()
            player_data = self.player_manager.get_player_data()

            warning_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{player_data['name']}</b><br><br>"
            warning_text += f"<span style='color: rgb(255, 100, 100); font-size: 22px;'>You need to select all 6 actions before starting, ma-a-n!</span><br><br>"
            warning_text += f"Missing: {missing} action{'s' if missing > 1 else ''}"

            self.dialogText.setText(warning_text)
            self.DialogBox.verticalScrollBar().setValue(0)

            # Pokaż awatar gracza
            pixmap = self.avatar_image.pixmap()
            if pixmap is not None and not pixmap.isNull():
                scaled_pixmap = self.avatar_image.scaled(
                    self.avatar_image.width(), self.avatar_image.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.avatar_image.setPixmap(scaled_pixmap)
        else:
            self.game_started = True
            self.unspent_money = self.player_manager.get_player_balance()
            self.main_window.settings_page.disable_difficulty_buttons()
            self.turn_counter = 0
            for widget in self.action_manager.action_widgets:
                widget.hide_controls()
            self.update_turn_display()

            # Ukryj Random i Start, pokaż Continue
            self.btn_random.hide()
            self.btn_start.hide()
            self.btn_continue.show()

            # Pokaż komunikat o rozpoczęciu gry
            player_data = self.player_manager.get_player_data()
            start_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{player_data['name']}</b><br><br>"
            start_text += f"<span style='color: rgb(100, 255, 100); font-size: 22px;'>Great! All actions selected. The game has begun! The first turn is finished.</span><br><br>"
            start_text += f"Selected actions: {', '.join(self.action_manager.get_selected_actions())}"


            self.dialogText.setText(start_text)
            self.DialogBox.verticalScrollBar().setValue(0)

    def continue_game(self):
        # Zwiększ licznik tur
        self.turn_counter += 1
        self.update_turn_display()

        if self.turn_counter >= self.max_turns:
            self.game_over()
        else:
            # Kontynuuj grę normalnie
            player_data = self.player_manager.get_player_data()
            continue_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{player_data['name']}</b><br><br>"
            continue_text += f"Turn {self.turn_counter+1} of {self.max_turns+1}<br><br>"
            continue_text += "continues..."

            self.dialogText.setText(continue_text)
            self.DialogBox.verticalScrollBar().setValue(0)

    def game_over(self):
        """Wyświetla okno Game Over i resetuje grę"""
        player_data = self.player_manager.get_player_data()
        final_balance = self.player_manager.get_player_balance()

        dialog = GameOverDialog(self, player_data['name'], final_balance)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.main_window.show_menu()
        else:
            self.reset_game()


    def reset_game(self):
        """Reset the game to the initial state."""
        self.game_started = False
        self.turn_counter = 0
        clear_stock_files()
        self.unspent_money = None

        # --- Reset player balance based on current difficulty ---
        difficulty = self.main_window.settings_page.get_difficulty_id()
        if difficulty == 1:
            self.player_manager.set_player_balance(2400)
        elif difficulty == 2:
            self.player_manager.set_player_balance(1200)
        else:
            self.player_manager.set_player_balance(600)

        # Update balance display
        self.balance.setText(f"$ {self.player_manager.get_player_balance()}")

        # Reset action selections
        self.action_manager.reset_selections()
        for widget in self.action_manager.action_widgets:
            widget.show_controls()

        # Show Random and Start buttons, hide Continue
        self.btn_random.show()
        self.btn_start.show()
        self.btn_continue.hide()

        # Enable difficulty selection
        self.main_window.settings_page.enable_difficulty_buttons()

        # Show player character and reset dialog
        self.show_player_character()

        player_data = self.player_manager.get_player_data()
        reset_text = f"<b style='color: rgb(255, 215, 0); font-size: 30px;'>{player_data['name']}</b><br><br>"
        reset_text += "Ready for a new game! Select your actions and press Start."

        self.dialogText.setText(reset_text)
        self.DialogBox.verticalScrollBar().setValue(0)