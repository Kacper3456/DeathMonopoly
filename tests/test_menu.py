import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QPushButton
from game.menu import MenuPage

@pytest.fixture
def mock_main_window(qtbot):
    """Fixture that returns a mock main_window with expected methods."""
    mock = MagicMock()
    mock.show_game = MagicMock()
    mock.show_settings = MagicMock()
    return mock

@pytest.fixture
def menu_page(mock_main_window, qtbot):
    """Fixture that creates a MenuPage instance without showing GUI."""
    menu = MenuPage(mock_main_window)
    qtbot.addWidget(menu)  # add widget to qtbot for proper cleanup
    return menu

#czy w menu są wszystkie 3 przyciski
def test_buttons_created(menu_page):
    buttons = [child for child in menu_page.menu_box.children() if isinstance(child, QPushButton)]
    assert len(buttons) == 3, "MenuPage should have 3 buttons"

#Czy przycisk START poprawnie wywołuje main_window.show_game
def test_start_button_calls_show_game(menu_page):
    """START button should call main_window.show_game."""
    start_btn = [b for b in menu_page.menu_box.children() if isinstance(b, QPushButton)][0]
    start_btn.clicked.emit()
    menu_page.main_window.show_game.assert_called_once()

def test_settings_button_calls_show_settings(menu_page):
    """SETTINGS button should call main_window.show_settings."""
    settings_btn = [b for b in menu_page.menu_box.children() if isinstance(b, QPushButton)][1]
    settings_btn.clicked.emit()
    menu_page.main_window.show_settings.assert_called_once()

def test_quit_button_calls_qapplication_quit(monkeypatch, menu_page):
    """QUIT button should call QApplication.quit."""
    called = {}

    # Patch QApplication.instance().quit to record call
    class DummyApp:
        def quit(self_inner):
            called["quit"] = True

    monkeypatch.setattr("PySide6.QtWidgets.QApplication.instance", lambda: DummyApp())

    quit_btn = [b for b in menu_page.menu_box.children() if isinstance(b, QPushButton)][2]
    quit_btn.clicked.emit()
    assert called.get("quit") is True

def test_resizeEvent_changes_background_size(menu_page):
    """resizeEvent should resize the background label."""
    original_size = menu_page.background.size()
    # Simulate resize
    class DummyEvent:
        def size(self_inner):
            class DummySize:
                def width(self_inner2):
                    return 500
                def height(self_inner2):
                    return 400
            return DummySize()
    menu_page.resizeEvent(DummyEvent())
    assert menu_page.background.width() == 500
    assert menu_page.background.height() == 400