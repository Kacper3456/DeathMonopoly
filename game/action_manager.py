from PySide6.QtWidgets import QLabel, QMenu
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Signal, Qt, QPoint
import random
from game.stock_data import get_price_change

class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class ActionWidget(QLabel):
    valueChanged = Signal(int)

    def __init__(self, parent=None, player_manager=None, balance_label=None):
        super().__init__(parent)

        self.player_manager = player_manager  # reference to PlayerManager
        self.balance_label = balance_label    # QLabel to display balance

        self.quantity = 0
        self.allow_click = True

        # --- Main image label ---
        self.image_label = ClickableLabel(self)
        self.image_label.setGeometry(40, 0, 260, 160)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)

        # --- Minus button ---
        self.minus_btn = ClickableLabel(self)
        self.minus_btn.setGeometry(0, 60, 40, 40)
        self.minus_btn.setText("-")
        self.minus_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minus_btn.setStyleSheet("background: #aa4444; color: white; font-size: 20px;")
        self.minus_btn.clicked.connect(self.decrease_value)

        # --- Plus button ---
        self.plus_btn = ClickableLabel(self)
        self.plus_btn.setGeometry(300, 60, 40, 40)
        self.plus_btn.setText("+")
        self.plus_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plus_btn.setStyleSheet("background: #44aa44; color: white; font-size: 20px;")
        self.plus_btn.clicked.connect(self.increase_value)

        # --- Value label ---
        self.value_label = QLabel("0", self)
        self.value_label.setGeometry(0, 160, 340, 20)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 18px;")

    # -----------------------------------
    # Zmiana wartości
    # -----------------------------------
    def increase_value(self):
        if not self.allow_click or not self.player_manager:
            return

        player_balance = self.player_manager.get_player_balance()
        if player_balance >= 100:  # adjust 100 if needed
            self.quantity += 100
            self.value_label.setText(str(self.quantity))

            # Decrease balance in PlayerManager
            self.player_manager.set_player_balance(player_balance - 100)

            # Update balance display
            if self.balance_label:
                self.balance_label.setText(f"$ {self.player_manager.get_player_balance()}")

    def decrease_value(self):
        if not self.allow_click or not self.player_manager:
            return

        if self.quantity > 0:
            self.quantity -= 100
            self.value_label.setText(str(self.quantity))

            # Refund money in PlayerManager
            player_balance = self.player_manager.get_player_balance()
            self.player_manager.set_player_balance(player_balance + 100)

            # Update balance display
            if self.balance_label:
                self.balance_label.setText(f"$ {self.player_manager.get_player_balance()}")

    # -----------------------------------
    # Ustawianie obrazka
    # -----------------------------------
    def set_pixmap(self, pixmap: QPixmap):
        self.image_label.setPixmap(pixmap)

    def hide_controls(self):
        self.plus_btn.hide()
        self.minus_btn.hide()

    def show_controls(self):
        self.quantity = 0
        self.value_label.setText(str(self.quantity))

        self.plus_btn.show()
        self.minus_btn.show()


class ActionManager:
    def __init__(self):
        # Opcje dostępne w menu
        self.options = {
            "AAPL": "images/stocks/apple_logo.png",
            "GOOG": "images/stocks/google_logo.png",
            "MSFT": "images/stocks/microsoft_logo.png",
            "NVDA": "images/stocks/nvidia_logo.png",
            "AMZN": "images/stocks/amazon_logo.png",
            "TSLA": "images/stocks/tesla_logo.png",
            "META": "images/stocks/meta_logo.png",
            "CSCO": "images/stocks/cisco_logo.png",
            "PEP": "images/stocks/pepsico_logo.png",
            "NFLX": "images/stocks/netflix_logo.png",
            "EA": "images/stocks/ea_logo.png",
        }
        
        # Współrzędne dla opcji akcyjnych - ZMNIEJSZONE
        self.action_x_start = 30
        self.action_y_start = 55
        self.action_width = 340 
        self.action_height = 180
        self.action_padding = 10
        
        # Lista utworzonych widgetów
        self.action_widgets = []
        
        # Śledzenie wyborów gracza (None = nie wybrano, string = wybrana opcja)
        self.selected_actions = [None] * 6

    def create_action_widgets(self, parent, player_manager=None, balance_label=None):
        self.action_widgets = []

        positions = [
            (self.action_x_start, self.action_y_start),
            (self.action_x_start + self.action_width + self.action_padding, self.action_y_start),
            (self.action_x_start + 2 * self.action_width + 2 * self.action_padding, self.action_y_start),
            (self.action_x_start, self.action_y_start + self.action_height + self.action_padding),
            (self.action_x_start + self.action_width + self.action_padding,
             self.action_y_start + self.action_height + self.action_padding),
            (self.action_x_start + 2 * self.action_width + 2 * self.action_padding,
             self.action_y_start + self.action_height + self.action_padding),
        ]

        for i, (x, y) in enumerate(positions):
            action = ActionWidget(parent, player_manager=player_manager, balance_label=balance_label)
            action.setGeometry(x, y, self.action_width, self.action_height)
            action.setProperty("action_index", i)
            action.image_label.setProperty("action_index", i)

            pixmap = QPixmap("images/game_window/placeholder.png")
            action.set_pixmap(pixmap)

            self.action_widgets.append(action)

        return self.action_widgets
    
    def get_available_options(self):
        #Zwraca listę opcji, które jeszcze nie zostały wybrane
        return [name for name in self.options.keys() 
                if name not in self.selected_actions]
    
    def show_action_menu(self, target_label, parent_widget):
        """
        Wyświetla menu z opcjami dla danej akcji
        
        Args:
            target_label: Label, na którym kliknięto
            parent_widget: Widget rodzic dla menu
        """
        menu = QMenu(parent_widget)
        action_index = target_label.property("action_index")
        if action_index is None:
            print("Warning: action_index is None for the clicked label.")
            return
        current_selection = self.selected_actions[action_index]

        
        # Dodaj opcje do menu
        for name in self.options.keys():
            action = QAction(name, menu)
            
            # Jeśli opcja jest już wybrana w innym miejscu (ale nie w tym)
            if name in self.selected_actions and name != current_selection:
                action.setEnabled(False)  # Zablokuj opcję (będzie szara)
            
            menu.addAction(action)
        
        # Pokaż menu pod klikniętym labelem
        pos = target_label.mapToGlobal(QPoint(0, target_label.height()))
        selected_action = menu.exec_(pos)
        
        # Jeśli wybrano opcję, zmień obrazek
        if selected_action:
            choice = selected_action.text()
            image_path = self.options.get(choice)
            if image_path:
                pixmap = QPixmap(image_path)
                target_label.setPixmap(pixmap)
                
                # Zapisz wybór
                action_index = target_label.property("action_index")
                self.selected_actions[action_index] = choice
    
    def randomize_actions(self):
        """Losowo wybiera opcje dla wszystkich 6 akcji"""
        # Sprawdź czy mamy wystarczająco opcji
        if len(self.options) < 6:
            print("Zbyt mało opcji do losowania!")
            return
            
             # Losuj 6 unikalnych opcji
        available_choices = list(self.options.keys())
        selected_choices = random.sample(available_choices, 6)
        
        for i, action_widget in enumerate(self.action_widgets):
            choice = selected_choices[i]
            image_path = self.options[choice]
            
            # Ustaw obrazek
            pixmap = QPixmap(image_path)
            action_widget.set_pixmap(pixmap)
            
            # Zapisz wybór
            self.selected_actions[i] = choice
    
    def all_actions_selected(self):
        return all(action is not None for action in self.selected_actions)
    
    def get_missing_count(self):
        return self.selected_actions.count(None)

    def reset_selections(self):
        self.selected_actions = [None] * 6
        for action_widget in self.action_widgets:
            # Reset image to placeholder
            pixmap = QPixmap("images/game_window/placeholder.png")
            action_widget.set_pixmap(pixmap)

            # Reset value label and quantity
            action_widget.quantity = 0
            action_widget.value_label.setText("0")
    
    def add_option(self, name, image_path):
        self.options[name] = image_path
    
    def remove_option(self, name):
        if name in self.options:
            del self.options[name]
    
    def get_options(self):
        return self.options
    
    def get_selected_actions(self):
        return self.selected_actions

    def update_selected_action_charts(self):
        """Zamienia obrazki wybranych akcji na wygenerowane wykresy."""
        for i, choice in enumerate(self.selected_actions):
            if choice:
                chart_path = f"Stock_charts/{choice}_chart.png"
                pixmap = QPixmap(chart_path)
                if not pixmap.isNull():
                    self.action_widgets[i].image_label.setPixmap(pixmap)

    def update_value_labels_by_stock(self):
        """
        Updates each ActionWidget value based on stock performance.
        """
        for i, stock_name in enumerate(self.selected_actions):
            if stock_name is None:
                continue

            action_widget = self.action_widgets[i]
            multiplier = get_price_change(stock_name)

            # Update value
            new_value = int(action_widget.quantity * multiplier)
            action_widget.quantity = new_value
            action_widget.value_label.setText(str(new_value))