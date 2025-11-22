from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt
from AI import ask_bot


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
            {"name": "BORIS", "avatar": "images/game_window/avatar/russian_spy.png", "dialogue": "I am Boris and of course I am NOT a Russian spy and I do NOT want to steal all your money"},
            {"name": "WARIO", "avatar": "images/game_window/avatar/wario.png", "dialogue": "Relax, take-a the spaghetti, life is good"},
            {"name": "ALBEDO", "avatar": "images/game_window/avatar/succubus.png", "dialogue": "Just say the word, and I will prepare a strategy so perfect that even the demons of the abyss won't dare to question your market dominance"},
            {"name": "GERALT", "avatar": "images/game_window/avatar/geralt.png", "dialogue": "Monsters? Trends? Speculative bubbles? No problem. Just keep in mind—if something goes wrong, it's not my fault. The world is broken, not me"},
            {"name": "JADWIDA", "avatar": "images/game_window/avatar/queen.png", "dialogue": "Sometimes it's good to watch how the mortal crowd panics on the market. At least that can be entertaining. But since you are already here, maybe you can tell me what you intend to invest in?"}
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
        self.unselect_npc()
        
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
    
    def unselect_npc(self):
        if self.selected_index is not None:
            self.npc_widgets[self.selected_index].set_selected(False)
            self.selected_index = None

    def update_dialog_ai(self, index, player_balance=None, selected_companies=None):
        """
        Updates the 'dialogue' field of the NPC at `index` using AI.
        This does not touch GUI; GamePage.update_npc_display will show the new text automatically.
        """
        if not (0 <= index < len(self.npc_data_list)):
            return

        # Prepare input for AI
        question = "Based on budget and the data from selected companies choose what to invest in. remember to be biased for japanese and italian related companies"
        if player_balance is not None:
            question += f"Budget: {player_balance}\n"
        if selected_companies is not None:
            question += f"Selected companies: {', '.join(selected_companies)}"

        # Generate AI response
        ai_response = ask_bot(question)

        # Update the NPC dialogue
        self.npc_data_list[index]['dialogue'] = ai_response
