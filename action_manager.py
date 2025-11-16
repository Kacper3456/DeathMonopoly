from PySide6.QtWidgets import QLabel, QMenu
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal, Qt, QPoint


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class ActionManager:
    def __init__(self):
        self.options = {
            "easy": "images/options/easy.png",
            "hard": "images/options/hard.png",
            "las": "images/options/las.png",
            "music": "images/options/music.png",
            "medium": "images/options/medium.png",
        }
        
        self.action_x_start = 30
        self.action_y_start = 55
        self.action_width = 330
        self.action_height = 200
        self.action_padding = 20
        
        # Lista utworzonych widgetów
        self.action_widgets = []
    
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
        
        for i, (x, y) in enumerate(positions, 1):
            action = ClickableLabel("START", parent)
            action.setGeometry(x, y, self.action_width, self.action_height)
            
            pixmap = QPixmap("images/game_window/placeholder.png")
            scaled_pixmap = pixmap.scaled(action.width(), action.height())
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
                scaled_pixmap = pixmap.scaled(target_label.width(), target_label.height())
                target_label.setPixmap(scaled_pixmap)
    
    def add_option(self, name, image_path):
        self.options[name] = image_path
    
    def remove_option(self, name):
        if name in self.options:
            del self.options[name]
    
    def get_options(self):
        return self.options