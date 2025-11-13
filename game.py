from PySide6.QtWidgets import QWidget, QLabel, QGroupBox, QScrollArea, QMenu, QPushButton
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Signal, Qt, QPoint


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class GamePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Okno Gry")

        # --- współrzędne dla Opcji akcyjnych ---
        action_x_start = 10
        action_y_start = 20
        action_width = 330
        action_height = 200
        action_padding = 21

        # --- Tło gry ---
        self.background = QLabel(self)
        pixmap = QPixmap("program_files/stars.png")
        self.background.setPixmap(pixmap)
        self.background.setScaledContents(True)
        self.background.resize(self.size())

        # --- Box do grupowania opcji aukcyjnych ---
        self.menu_box = QGroupBox(self)
        self.menu_box.setStyleSheet("QGroupBox { border: none; }")
        self.menu_box.setGeometry(20, 30, 1050, 800)

        # Opcja Akcyjna 1
        self.action1 = ClickableLabel("START", self.menu_box)
        self.action1.setGeometry(action_x_start, action_y_start, action_width, action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action1.width(), self.action1.height())
        self.action1.setPixmap(scaled_pixmap)
        self.action1.clicked.connect(lambda checked=False: self.show_action_menu(self.action1))

        # Opcja Akcyjna 2
        self.action2 = ClickableLabel("START", self.menu_box)
        self.action2.setGeometry(action_x_start + action_width + action_padding, action_y_start, action_width, action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action2.width(), self.action2.height())
        self.action2.setPixmap(scaled_pixmap)
        self.action2.clicked.connect(lambda checked=False: self.show_action_menu(self.action2))

        # Opcja Akcyjna 3
        self.action3 = ClickableLabel("START", self.menu_box)
        self.action3.setGeometry(action_x_start + 2 * action_width + 2 * action_padding, action_y_start, action_width,
                            action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action3.width(), self.action3.height())
        self.action3.setPixmap(scaled_pixmap)
        self.action3.clicked.connect(lambda checked=False: self.show_action_menu(self.action3))

        # Opcja Akcyjna 4
        self.action4 = ClickableLabel("START", self.menu_box)
        self.action4.setGeometry(action_x_start, action_y_start + action_height + action_padding, action_width,
                            action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action4.width(), self.action4.height())
        self.action4.setPixmap(scaled_pixmap)
        self.action4.clicked.connect(lambda checked=False: self.show_action_menu(self.action4))

        # Opcja Akcyjna 5
        self.action5 = ClickableLabel("START", self.menu_box)
        self.action5.setGeometry(action_x_start + action_width + action_padding, action_y_start + action_height + action_padding, action_width, action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action5.width(), self.action5.height())
        self.action5.setPixmap(scaled_pixmap)
        self.action5.clicked.connect(lambda checked=False: self.show_action_menu(self.action5))

        # Opcja Akcyjna 6
        self.action6 = ClickableLabel("START", self.menu_box)
        self.action6.setGeometry(action_x_start + 2 * action_width + 2 * action_padding, action_y_start + action_height + action_padding, action_width, action_height)
        pixmap = QPixmap("images/options/Placeholder_addimage.png")
        scaled_pixmap = pixmap.scaled(self.action6.width(), self.action6.height())
        self.action6.setPixmap(scaled_pixmap)
        self.action6.clicked.connect(lambda checked=False: self.show_action_menu(self.action6))

        # --- Avatar Box ---
        self.avatarBox = QLabel(self)
        self.avatarBox.setGeometry(1100, 500, 250, 250)
        self.avatarBox.setStyleSheet("QLabel { background-color: rgba(128, 0, 128, 200); }")
        avatar_image = QLabel(self.avatarBox)
        avatar_image.setGeometry(25, 25, 200, 200)
        pixmap = QPixmap("images/options/las.png")
        scaled_pixmap = pixmap.scaled(avatar_image.width(), avatar_image.height())
        avatar_image.setPixmap(scaled_pixmap)

        # --- Dialog Box (scrollable container) ---
        self.DialogBox = QScrollArea(self)
        self.DialogBox.setGeometry(30, 500, 1035, 250)
        self.DialogBox.setStyleSheet("""
            QScrollArea {
                background-color: rgba(128, 0, 128, 128);
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
        self.dialogText.setFont(QFont("Arial", 16))
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

        # --- Players Box ---
        self.playerBox = QLabel(self)
        self.playerBox.setGeometry(1100, 110, 250, 360)
        self.playerBox.setStyleSheet("QLabel { background-color: rgba(128, 0, 128, 200); }")

        # --- Currency Box ---
        self.currencyBox = QLabel(self)
        self.currencyBox.setGeometry(1100, 50, 250, 40)
        self.currencyBox.setStyleSheet("QLabel { background-color: rgba(128, 0, 128, 200); }")
        
        
        # # --- przycisk wyjście do menu ---
        # btn_exit = QPushButton(self.menu_box)
        # btn_exit.setGeometry(1000, 0, 48, 30)
        # btn_exit.clicked.connect(self.main_window.show_menu)
        # btn_exit.setStyleSheet(f"""
        #         QPushButton {{
        #             background-image: url("images/buttons/exit-button.png");
        #             background-position: center;
        #             border-radius: 10px;
        #         }}
        #         QPushButton:hover {{
        #             background-color: rgba(255, 215, 0, 0.7);
        #         }}
        #         QPushButton:pressed {{
        #             background-color: orange;
        #         }}
        #     """)

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

    def show_action_menu(self, target_label):
        menu = QMenu(self)

        # Example options
        options = {
            "easy": "images/options/easy.png",
            "hard": "images/options/hard.png",
            "las": "images/options/las.png",
            "music": "images/options/music.png",
            "medium": "images/options/medium.png",
        }

        # Add items dynamically
        for name in options.keys():
            menu.addAction(name)

            # Show menu under the clicked label
        pos = target_label.mapToGlobal(QPoint(0, target_label.height()))
        selected_action = menu.exec_(pos)

        if selected_action:
            choice = selected_action.text()
            image_path = options.get(choice)
            if image_path:
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(target_label.width(), target_label.height())
                target_label.setPixmap(scaled_pixmap)