from PySide6.QtWidgets import QLabel, QMenu
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal, Qt, QPoint
import random


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class ActionManager:
    def __init__(self):
        # Opcje dostępne w menu
        self.options = {
            "easy": "images/options/easy.png",
            "hard": "images/options/hard.png",
            "las": "images/options/las.png",
            "music": "images/options/music.png",
            "medium": "images/options/medium.png",
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
    
    def create_action_widgets(self, parent):
        """
        Tworzy 6 opcji akcyjnych i zwraca je jako listę
        
        Args:
            parent: Widget rodzic (menu_box)
        
        Returns:
            Lista widgetów ClickableLabel
        """
        self.action_widgets = []
        
        # Definicja pozycji dla każdej opcji
        positions = [
            # Górny rząd
            (self.action_x_start, self.action_y_start),
            (self.action_x_start + self.action_width + self.action_padding, self.action_y_start),
            (self.action_x_start + 2 * self.action_width + 2 * self.action_padding, self.action_y_start),
            # Dolny rząd
            (self.action_x_start, self.action_y_start + self.action_height + self.action_padding),
            (self.action_x_start + self.action_width + self.action_padding, 
             self.action_y_start + self.action_height + self.action_padding),
            (self.action_x_start + 2 * self.action_width + 2 * self.action_padding, 
             self.action_y_start + self.action_height + self.action_padding),
        ]
        
        # Tworzenie widgetów
        for i, (x, y) in enumerate(positions, 1):
            action = ClickableLabel("START", parent)
            action.setGeometry(x, y, self.action_width, self.action_height)
            action.setProperty("action_index", i - 1)  # Zapisz indeks
            
            # Załaduj placeholder
            pixmap = QPixmap("images/game_window/placeholder.png")
            scaled_pixmap = pixmap.scaled(
                action.width(), action.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            action.setPixmap(scaled_pixmap)
            
            self.action_widgets.append(action)
        
        return self.action_widgets
    
    def show_action_menu(self, target_label, parent_widget):
        """
        Wyświetla menu z opcjami dla danej akcji
        
        Args:
            target_label: Label, na którym kliknięto
            parent_widget: Widget rodzic dla menu
        """
        menu = QMenu(parent_widget)
        
        # Dodaj opcje do menu
        for name in self.options.keys():
            menu.addAction(name)
        
        # Pokaż menu pod klikniętym labelem
        pos = target_label.mapToGlobal(QPoint(0, target_label.height()))
        selected_action = menu.exec_(pos)
        
        # Jeśli wybrano opcję, zmień obrazek
        if selected_action:
            choice = selected_action.text()
            image_path = self.options.get(choice)
            if image_path:
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(
                    target_label.width(), target_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                target_label.setPixmap(scaled_pixmap)
                
                # Zapisz wybór
                action_index = target_label.property("action_index")
                self.selected_actions[action_index] = choice
    
    def randomize_actions(self):
        """Losowo wybiera opcje dla wszystkich 6 akcji"""
        for i, action_widget in enumerate(self.action_widgets):
            # Losuj opcję
            choice = random.choice(list(self.options.keys()))
            image_path = self.options[choice]
            
            # Ustaw obrazek
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                action_widget.width(), action_widget.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            action_widget.setPixmap(scaled_pixmap)
            
            # Zapisz wybór
            self.selected_actions[i] = choice
    
    def all_actions_selected(self):
        return all(action is not None for action in self.selected_actions)
    
    def get_missing_count(self):
        return self.selected_actions.count(None)
    
    def reset_selections(self):
        self.selected_actions = [None] * 6
        for action_widget in self.action_widgets:
            pixmap = QPixmap("images/game_window/placeholder.png")
            scaled_pixmap = pixmap.scaled(
                action_widget.width(), action_widget.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            action_widget.setPixmap(scaled_pixmap)
    
    def add_option(self, name, image_path):
        self.options[name] = image_path
    
    def remove_option(self, name):
        if name in self.options:
            del self.options[name]
    
    def get_options(self):
        return self.options
    
    def get_selected_actions(self):
        return self.selected_actions