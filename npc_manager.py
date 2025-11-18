from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt


class NPCWidget(QWidget):
    clicked = Signal(int)
    
    def __init__(self, npc_data, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.npc_data = npc_data
        self.is_selected = False
        
        # --- Ustawienia kontenera ----
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(230, 70)
        
        # --- Awatar ---
        self.avatar_image = QLabel(self)
        self.avatar_image.setGeometry(5, 5, 65, 65)
        pixmap = QPixmap(npc_data["avatar"])
        if pixmap.isNull():
            pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(67, 67, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.avatar_image.setPixmap(scaled_pixmap)
        self.avatar_image.setStyleSheet("border: 2px solid rgba(255, 215, 0, 0.7); border-radius: 5px;")
        
        # --- Imię ---
        self.nickname_label = QLabel(npc_data["name"], self)
        self.nickname_label.setGeometry(85, 10, 160, 30)
        self.nickname_label.setFont(QFont("Helvetica", 22, QFont.Weight.Bold))
        self.nickname_label.setStyleSheet("color: white; background-color: transparent;")
        self.nickname_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
    
    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            self.nickname_label.setStyleSheet("color: rgb(255, 215, 0); background-color: transparent;")
        else:
            self.nickname_label.setStyleSheet("color: white; background-color: transparent;")


class NPCManager:
    
    def __init__(self):
        self.npc_data_list = [
            {"name": "BORIS", "avatar": "images/game_window/avatar/russian_spy.png", "dialogue": "Jestem Boris i oczywiście NIE jestem ruskim szpiegiem i NIE chcę ukraść wszystkich Twoich pieniędzy"},
            {"name": "WARIO", "avatar": "images/game_window/avatar/wario.png", "dialogue": "Relax, take-a the spaghetti, life is good"},
            {"name": "ALBEDO", "avatar": "images/game_window/avatar/succubus.png", "dialogue": "Powiedz tylko słowo, a przygotuję strategię tak doskonałą, że nawet demony z otchłani nie odważą się zakwestionować Twojej dominacji na rynku"},
            {"name": "GERALT", "avatar": "images/game_window/avatar/geralt.png", "dialogue": "Potwory? Trendy? Bańki spekulacyjne? Żaden problem. Tylko miej na uwadze — jak się coś sypnie, to nie moja wina. To świat jest popsuty, nie ja"},
            {"name": "JADWIDA", "avatar": "images/game_window/avatar/queen.png", "dialogue": "Czasem dobrze spojrzeć, jak tłum śmiertelników panikuje na rynku. To przynajmniej bywa zabawne. Ale skoro już tu jesteś, może opowiesz mi, w co zamierzasz inwestować?"}
        ]
        
        self.npc_widgets = []
        self.selected_index = None
    
    def create_npc_widgets(self, parent_widget):
        npc_spacing = 70
        
        for i, npc_data in enumerate(self.npc_data_list):
            npc_widget = NPCWidget(npc_data, i, parent_widget)
            npc_widget.move(10, 10 + i * npc_spacing)
            npc_widget.clicked.connect(self.on_npc_clicked)
            self.npc_widgets.append(npc_widget)
        
        return self.npc_widgets
    
    def on_npc_clicked(self, index):
        
        # Odznacz poprzedniego
        if self.selected_index is not None:
            self.npc_widgets[self.selected_index].set_selected(False)
        
        # Zaznacz nowego
        self.selected_index = index
        self.npc_widgets[index].set_selected(True)
    
    def get_selected_npc_data(self):
        if self.selected_index is not None:
            return self.npc_data_list[self.selected_index]
        return None
    
    def get_npc_data(self, index):
        if 0 <= index < len(self.npc_data_list):
            return self.npc_data_list[index]
        return None