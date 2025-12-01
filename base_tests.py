import pytest
import os
import csv
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from datetime import datetime
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap

# Import game modules
from Game_code.player_manager import PlayerManager
from Game_code.action_manager import ActionManager, ActionWidget, ClickableLabel
from Game_code.npc_manager import NPCManager, NPCWidget
from Game_code.stock_data import (
    get_turn_dates,
    get_price_change,
    clear_stock_files,
    CSV_DIR,
    CHART_DIR,
    get_data,
    get_data_chart,
    generate_all_charts
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def qtbot(qapp):
    from pytestqt.qtbot import QtBot
    return QtBot(qapp)


@pytest.fixture
def player_manager():
    return PlayerManager()


@pytest.fixture
def action_manager():
    return ActionManager()


@pytest.fixture
def npc_manager():
    return NPCManager()


@pytest.fixture
def temp_csv_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_history.csv') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Close', 'Open', 'High', 'Low'])
        writer.writerow(['2024-01-01', '100.0', '98.0', '102.0', '97.0'])
        writer.writerow(['2024-01-02', '105.0', '100.0', '106.0', '99.0'])
        writer.writerow(['2024-01-03', '110.0', '105.0', '111.0', '104.0'])
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.remove(temp_path)


# ============================================================================
# PlayerManager Tests (40 tests)
# ============================================================================

class TestPlayerManagerBasics:

    def test_initial_balance_default(self, player_manager):
        # Verifies that a new PlayerManager instance starts with the default balance of 2400
        assert player_manager.get_player_balance() == 2400

    def test_initial_name_default(self, player_manager):
        # Verifies that the player's default name is set to "Waldemar" on initialization
        assert player_manager.get_player_data()["name"] == "Waldemar"

    def test_initial_avatar_default(self, player_manager):
        # Checks that the default avatar path points to the businessman image
        assert player_manager.get_player_data()["avatar"] == "images/game_window/avatar/businessman.png"

    def test_initial_dialogue_exists(self, player_manager):
        # Ensures that the player has a non-empty dialogue string by default
        assert len(player_manager.get_player_data()["dialogue"]) > 0

    def test_player_data_structure(self, player_manager):
        # Validates that player_data contains all required keys: name, avatar, dialogue, balance
        data = player_manager.get_player_data()
        assert "name" in data
        assert "avatar" in data
        assert "dialogue" in data
        assert "balance" in data

    def test_get_player_data_returns_dict(self, player_manager):
        # Confirms that get_player_data() returns a dictionary type
        assert isinstance(player_manager.get_player_data(), dict)

    def test_player_data_not_none(self, player_manager):
        # Ensures that the player_data attribute is never None
        assert player_manager.player_data is not None


class TestPlayerManagerBalance:

    def test_set_balance_positive(self, player_manager):
        # Tests setting the player balance to a positive value and retrieving it
        player_manager.set_player_balance(5000)
        assert player_manager.get_player_balance() == 5000

    def test_set_balance_zero(self, player_manager):
        # Verifies that balance can be set to zero without issues
        player_manager.set_player_balance(0)
        assert player_manager.get_player_balance() == 0

    def test_set_balance_negative(self, player_manager):
        # Tests that negative balances are allowed (for debt/losses)
        player_manager.set_player_balance(-100)
        assert player_manager.get_player_balance() == -100

    def test_set_balance_large_number(self, player_manager):
        # Checks that very large balance values (1,000,000) can be stored
        player_manager.set_player_balance(1000000)
        assert player_manager.get_player_balance() == 1000000

    def test_set_balance_float(self, player_manager):
        # Verifies that float/decimal balance values are supported
        player_manager.set_player_balance(2500.50)
        assert player_manager.get_player_balance() == 2500.50

    def test_balance_persistence(self, player_manager):
        # Ensures balance persists after other player data operations
        player_manager.set_player_balance(1000)
        player_manager.set_player_name("Test")
        assert player_manager.get_player_balance() == 1000

    def test_multiple_balance_changes(self, player_manager):
        # Tests that consecutive balance updates work correctly
        player_manager.set_player_balance(100)
        player_manager.set_player_balance(200)
        player_manager.set_player_balance(300)
        assert player_manager.get_player_balance() == 300


class TestPlayerManagerName:

    def test_set_name_string(self, player_manager):
        # Verifies that player name can be set to a regular string value
        player_manager.set_player_name("John")
        assert player_manager.get_player_data()["name"] == "John"

    def test_set_name_empty_string(self, player_manager):
        # Tests that empty string is accepted as a valid name
        player_manager.set_player_name("")
        assert player_manager.get_player_data()["name"] == ""

    def test_set_name_with_spaces(self, player_manager):
        # Checks that names with spaces are handled correctly
        player_manager.set_player_name("John Doe")
        assert player_manager.get_player_data()["name"] == "John Doe"

    def test_set_name_with_special_chars(self, player_manager):
        # Verifies support for special characters and Unicode in names
        player_manager.set_player_name("Müller-Öström")
        assert player_manager.get_player_data()["name"] == "Müller-Öström"

    def test_set_name_very_long(self, player_manager):
        # Tests that very long names (100+ characters) can be stored
        long_name = "A" * 100
        player_manager.set_player_name(long_name)
        assert player_manager.get_player_data()["name"] == long_name

    def test_name_with_numbers(self, player_manager):
        # Checks that alphanumeric names are supported
        player_manager.set_player_name("Player123")
        assert player_manager.get_player_data()["name"] == "Player123"


class TestPlayerManagerAvatar:

    def test_set_avatar_path(self, player_manager):
        # Tests setting a custom avatar image path
        path = "images/test/avatar.png"
        player_manager.set_player_avatar(path)
        assert player_manager.get_player_data()["avatar"] == path

    def test_set_avatar_empty_path(self, player_manager):
        # Verifies that empty avatar path is accepted
        player_manager.set_player_avatar("")
        assert player_manager.get_player_data()["avatar"] == ""

    def test_set_avatar_absolute_path(self, player_manager):
        # Checks that absolute file paths work for avatars
        path = "/usr/share/images/avatar.png"
        player_manager.set_player_avatar(path)
        assert player_manager.get_player_data()["avatar"] == path

    def test_set_avatar_relative_path(self, player_manager):
        # Tests that relative paths are stored correctly
        path = "../avatars/test.png"
        player_manager.set_player_avatar(path)
        assert player_manager.get_player_data()["avatar"] == path


class TestPlayerManagerDialogue:

    def test_set_dialogue_string(self, player_manager):
        # Verifies that dialogue text can be set and retrieved
        dialogue = "Hello, world!"
        player_manager.set_player_dialogue(dialogue)
        assert player_manager.get_player_data()["dialogue"] == dialogue

    def test_set_dialogue_empty(self, player_manager):
        # Tests that empty dialogue string is accepted
        player_manager.set_player_dialogue("")
        assert player_manager.get_player_data()["dialogue"] == ""

    def test_set_dialogue_multiline(self, player_manager):
        # Checks that multiline dialogue with newlines works
        dialogue = "Line 1\nLine 2\nLine 3"
        player_manager.set_player_dialogue(dialogue)
        assert player_manager.get_player_data()["dialogue"] == dialogue

    def test_set_dialogue_very_long(self, player_manager):
        # Tests that very long dialogue text (500+ chars) is supported
        dialogue = "A" * 500
        player_manager.set_player_dialogue(dialogue)
        assert player_manager.get_player_data()["dialogue"] == dialogue


class TestPlayerManagerUpdate:

    def test_update_name_only(self, player_manager):
        # Tests partial update - only name is changed, other fields remain unchanged
        original_avatar = player_manager.get_player_data()["avatar"]
        player_manager.update_player_data(name="NewName")
        assert player_manager.get_player_data()["name"] == "NewName"
        assert player_manager.get_player_data()["avatar"] == original_avatar

    def test_update_avatar_only(self, player_manager):
        # Tests partial update - only avatar is changed
        original_name = player_manager.get_player_data()["name"]
        player_manager.update_player_data(avatar="new/path.png")
        assert player_manager.get_player_data()["avatar"] == "new/path.png"
        assert player_manager.get_player_data()["name"] == original_name

    def test_update_dialogue_only(self, player_manager):
        # Tests partial update - only dialogue is changed
        original_name = player_manager.get_player_data()["name"]
        player_manager.update_player_data(dialogue="New dialogue")
        assert player_manager.get_player_data()["dialogue"] == "New dialogue"
        assert player_manager.get_player_data()["name"] == original_name

    def test_update_all_fields(self, player_manager):
        # Verifies that all player fields can be updated in a single call
        player_manager.update_player_data(
            name="TestName",
            avatar="test.png",
            dialogue="Test dialogue"
        )
        data = player_manager.get_player_data()
        assert data["name"] == "TestName"
        assert data["avatar"] == "test.png"
        assert data["dialogue"] == "Test dialogue"

    def test_update_with_none_values(self, player_manager):
        # Ensures that None values don't overwrite existing data
        original_data = player_manager.get_player_data().copy()
        player_manager.update_player_data(name=None, avatar=None, dialogue=None)
        assert player_manager.get_player_data() == original_data

    def test_update_mixed_none_and_values(self, player_manager):
        # Tests updating some fields while keeping others unchanged using None
        player_manager.update_player_data(name="NewName", avatar=None, dialogue="New")
        assert player_manager.get_player_data()["name"] == "NewName"
        assert player_manager.get_player_data()["dialogue"] == "New"


# ============================================================================
# ActionManager Tests (60 tests)
# ============================================================================

class TestActionManagerInitialization:

    def test_options_count(self, action_manager):
        # Verifies that ActionManager initializes with 11 stock options
        assert len(action_manager.options) == 11

    def test_options_are_dict(self, action_manager):
        # Checks that options are stored in a dictionary structure
        assert isinstance(action_manager.options, dict)

    def test_specific_stocks_present(self, action_manager):
        # Validates that specific stock tickers (AAPL, GOOG, etc.) exist
        assert "AAPL" in action_manager.options
        assert "GOOG" in action_manager.options
        assert "MSFT" in action_manager.options
        assert "NVDA" in action_manager.options
        assert "AMZN" in action_manager.options

    def test_all_stocks_present(self, action_manager):
        # Ensures all 11 expected stock tickers are present
        expected = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA", "META", "CSCO", "PEP", "NFLX", "EA"]
        for stock in expected:
            assert stock in action_manager.options

    def test_initial_selected_actions(self, action_manager):
        # Verifies that no actions are selected on initialization
        assert action_manager.selected_actions == [None] * 6

    def test_selected_actions_length(self, action_manager):
        # Checks that selected_actions array has exactly 6 slots
        assert len(action_manager.selected_actions) == 6

    def test_action_widgets_empty_initially(self, action_manager):
        # Ensures action_widgets list starts empty before creation
        assert action_manager.action_widgets == []

    def test_position_coordinates(self, action_manager):
        # Validates that action widget position coordinates are set correctly
        assert action_manager.action_x_start == 30
        assert action_manager.action_y_start == 55

    def test_dimension_settings(self, action_manager):
        # Checks that action widget dimensions (width, height, padding) are defined
        assert action_manager.action_width == 340
        assert action_manager.action_height == 180
        assert action_manager.action_padding == 10


class TestActionManagerOptions:

    def test_get_options(self, action_manager):
        # Tests retrieving the complete dictionary of stock options
        options = action_manager.get_options()
        assert len(options) == 11
        assert isinstance(options, dict)

    def test_add_new_option(self, action_manager):
        # Verifies that new stock options can be added dynamically
        action_manager.add_option("TEST", "test/path.png")
        assert "TEST" in action_manager.options
        assert action_manager.options["TEST"] == "test/path.png"

    def test_add_multiple_options(self, action_manager):
        # Tests adding several new options sequentially
        action_manager.add_option("TEST1", "path1.png")
        action_manager.add_option("TEST2", "path2.png")
        assert "TEST1" in action_manager.options
        assert "TEST2" in action_manager.options

    def test_add_option_overwrites_existing(self, action_manager):
        # Checks that adding an option with existing key updates the path
        action_manager.add_option("AAPL", "new/path.png")
        assert action_manager.options["AAPL"] == "new/path.png"

    def test_remove_existing_option(self, action_manager):
        # Tests removing a stock option from the dictionary
        action_manager.remove_option("AAPL")
        assert "AAPL" not in action_manager.options

    def test_remove_nonexistent_option(self, action_manager):
        # Ensures removing non-existent option doesn't raise an error
        action_manager.remove_option("NONEXISTENT")  # Should not raise

    def test_remove_all_options(self, action_manager):
        # Verifies that all options can be removed, leaving empty dictionary
        for stock in list(action_manager.options.keys()):
            action_manager.remove_option(stock)
        assert len(action_manager.options) == 0


class TestActionManagerSelections:

    def test_all_actions_selected_when_none(self, action_manager):
        # Checks that all_actions_selected() returns False when nothing is selected
        assert not action_manager.all_actions_selected()

    def test_all_actions_selected_when_partial(self, action_manager):
        # Verifies False is returned when only some actions are selected
        action_manager.selected_actions[0] = "AAPL"
        action_manager.selected_actions[1] = "GOOG"
        assert not action_manager.all_actions_selected()

    def test_all_actions_selected_when_all(self, action_manager):
        # Tests that True is returned when all 6 actions are selected
        action_manager.selected_actions = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA"]
        assert action_manager.all_actions_selected()

    def test_get_missing_count_all_missing(self, action_manager):
        # Verifies count of 6 when no actions are selected
        assert action_manager.get_missing_count() == 6

    def test_get_missing_count_none_missing(self, action_manager):
        # Tests count of 0 when all actions are selected
        action_manager.selected_actions = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA"]
        assert action_manager.get_missing_count() == 0

    def test_get_missing_count_partial(self, action_manager):
        # Checks correct count when some actions are selected
        action_manager.selected_actions[0] = "AAPL"
        action_manager.selected_actions[1] = "GOOG"
        assert action_manager.get_missing_count() == 4

    def test_get_available_options_all_available(self, action_manager):
        # Tests that all 11 options are available when none selected
        available = action_manager.get_available_options()
        assert len(available) == 11

    def test_get_available_options_some_selected(self, action_manager):
        # Verifies available options exclude already selected ones
        action_manager.selected_actions[0] = "AAPL"
        action_manager.selected_actions[1] = "GOOG"
        available = action_manager.get_available_options()
        assert "AAPL" not in available
        assert "GOOG" not in available
        assert "MSFT" in available

    def test_get_available_options_all_selected(self, action_manager):
        # Checks remaining options when 6 are selected
        action_manager.selected_actions = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA"]
        available = action_manager.get_available_options()
        assert len(available) == 5  # 11 total - 6 selected

    def test_get_selected_actions(self, action_manager):
        # Tests retrieving the current selection array
        test_selections = ["AAPL", "GOOG", None, None, None, None]
        action_manager.selected_actions = test_selections
        assert action_manager.get_selected_actions() == test_selections

    def test_reset_selections_clears_all(self, action_manager):
        # Verifies that reset clears all 6 selection slots
        action_manager.selected_actions = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA"]
        action_manager.reset_selections()
        assert action_manager.selected_actions == [None] * 6

    def test_reset_selections_preserves_options(self, action_manager):
        # Ensures reset doesn't affect the available options dictionary
        original_options = action_manager.options.copy()
        action_manager.reset_selections()
        assert action_manager.options == original_options


class TestActionManagerWidgetCreation:

    def test_create_action_widgets_returns_list(self, action_manager, qapp):
        # Checks that widget creation returns a list
        parent = QWidget()
        widgets = action_manager.create_action_widgets(parent)
        assert isinstance(widgets, list)

    def test_create_action_widgets_correct_count(self, action_manager, qapp):
        # Verifies exactly 6 widgets are created
        parent = QWidget()
        widgets = action_manager.create_action_widgets(parent)
        assert len(widgets) == 6

    def test_create_action_widgets_stores_references(self, action_manager, qapp):
        # Tests that created widgets are stored in action_widgets list
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        assert len(action_manager.action_widgets) == 6

    def test_widget_has_correct_index_property(self, action_manager, qapp):
        # Ensures each widget has correct action_index property (0-5)
        parent = QWidget()
        widgets = action_manager.create_action_widgets(parent)
        for i, widget in enumerate(widgets):
            assert widget.property("action_index") == i


class TestActionManagerUpdateMethods:

    def test_update_selected_action_charts(self, action_manager, qapp):
        # Tests updating action widgets to display stock chart images
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        action_manager.selected_actions[0] = "AAPL"
        # Should not crash even if chart doesn't exist
        action_manager.update_selected_action_charts()

    def test_update_value_labels_by_stock_no_stock(self, action_manager, qapp):
        # Verifies update doesn't crash when no stocks are selected
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        # Should not raise error
        action_manager.update_value_labels_by_stock()

    @patch('Game_code.action_manager.get_price_change', return_value=1.5)
    def test_update_value_labels_by_stock_with_stock(self, mock_price, action_manager, qapp):
        # Tests value calculation based on stock price multiplier
        parent = QWidget()
        widgets = action_manager.create_action_widgets(parent)
        action_manager.selected_actions[0] = "AAPL"
        widgets[0].quantity = 100
        action_manager.update_value_labels_by_stock()
        assert widgets[0].quantity == 150  # 100 * 1.5


# ============================================================================
# ActionWidget Tests (40 tests)
# ============================================================================

class TestActionWidgetInitialization:

    def test_initial_quantity_zero(self, qapp):
        # Verifies that ActionWidget starts with quantity of 0
        parent = QWidget()
        widget = ActionWidget(parent)
        assert widget.quantity == 0

    def test_allow_click_true_initially(self, qapp):
        # Checks that click interactions are enabled by default
        parent = QWidget()
        widget = ActionWidget(parent)
        assert widget.allow_click is True

    def test_has_image_label(self, qapp):
        # Ensures widget has an image_label component for displaying stock logo
        parent = QWidget()
        widget = ActionWidget(parent)
        assert hasattr(widget, 'image_label')

    def test_has_minus_button(self, qapp):
        # Verifies widget has a minus button for decreasing investment
        parent = QWidget()
        widget = ActionWidget(parent)
        assert hasattr(widget, 'minus_btn')

    def test_has_plus_button(self, qapp):
        # Checks widget has a plus button for increasing investment
        parent = QWidget()
        widget = ActionWidget(parent)
        assert hasattr(widget, 'plus_btn')

    def test_has_value_label(self, qapp):
        # Ensures widget has a value_label to display current investment amount
        parent = QWidget()
        widget = ActionWidget(parent)
        assert hasattr(widget, 'value_label')

    def test_value_label_shows_zero(self, qapp):
        # Tests that value label displays "0" initially
        parent = QWidget()
        widget = ActionWidget(parent)
        assert widget.value_label.text() == "0"

    def test_player_manager_reference(self, qapp):
        # Verifies that PlayerManager reference is stored correctly
        parent = QWidget()
        pm = PlayerManager()
        widget = ActionWidget(parent, player_manager=pm)
        assert widget.player_manager is pm

    def test_balance_label_reference(self, qapp):
        # Checks that balance_label reference is stored for updates
        parent = QWidget()
        balance_label = QLabel()
        widget = ActionWidget(parent, balance_label=balance_label)
        assert widget.balance_label is balance_label


class TestActionWidgetIncreaseValue:

    def test_increase_value_insufficient_balance(self, qapp):
        # Tests that increase is blocked when player balance < 100
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(50)
        widget = ActionWidget(parent, player_manager=pm)
        widget.increase_value()
        assert widget.quantity == 0

    def test_increase_value_sufficient_balance(self, qapp):
        # Verifies quantity increases by 100 when sufficient balance exists
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        balance_label = QLabel()
        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.increase_value()
        assert widget.quantity == 100

    def test_increase_value_updates_balance(self, qapp):
        # Checks that player balance decreases by 100 after increase
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        balance_label = QLabel()
        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.increase_value()
        assert pm.get_player_balance() == 400

    def test_increase_value_updates_label(self, qapp):
        # Ensures value label updates to show new quantity
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        widget = ActionWidget(parent, player_manager=pm)
        widget.increase_value()
        assert widget.value_label.text() == "100"

    def test_increase_value_multiple_times(self, qapp):
        # Tests multiple consecutive increases and balance deductions
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(1000)
        widget = ActionWidget(parent, player_manager=pm)
        widget.increase_value()
        widget.increase_value()
        widget.increase_value()
        assert widget.quantity == 300
        assert pm.get_player_balance() == 700

    def test_increase_value_when_not_allowed(self, qapp):
        # Verifies increase is blocked when allow_click is False
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        widget = ActionWidget(parent, player_manager=pm)
        widget.allow_click = False
        widget.increase_value()
        assert widget.quantity == 0

    def test_increase_value_without_player_manager(self, qapp):
        # Tests that increase fails gracefully without PlayerManager
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.increase_value()
        assert widget.quantity == 0

    def test_increase_value_updates_balance_label_text(self, qapp):
        # Checks that balance display label updates with new value
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        balance_label = QLabel()
        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.increase_value()
        assert "400" in balance_label.text()


class TestActionWidgetDecreaseValue:

    def test_decrease_value_at_zero(self, qapp):
        # Verifies decrease doesn't go below 0 (no negative quantities)
        parent = QWidget()
        pm = PlayerManager()
        widget = ActionWidget(parent, player_manager=pm)
        widget.quantity = 0
        widget.decrease_value()
        assert widget.quantity == 0

    def test_decrease_value_from_positive(self, qapp):
        # Tests decreasing from a positive quantity value
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        balance_label = QLabel()
        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.quantity = 200
        widget.decrease_value()
        assert widget.quantity == 100

    def test_decrease_value_updates_balance(self, qapp):
        # Checks that balance is refunded when decreasing
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        balance_label = QLabel()
        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.quantity = 200
        widget.decrease_value()
        assert pm.get_player_balance() == 600

    def test_decrease_value_updates_label(self, qapp):
        # Ensures value label updates after decrease
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(500)
        widget = ActionWidget(parent, player_manager=pm)
        widget.quantity = 200
        widget.decrease_value()
        assert widget.value_label.text() == "100"

    def test_decrease_value_multiple_times(self, qapp):
        # Tests multiple consecutive decreases and refunds
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(100)
        widget = ActionWidget(parent, player_manager=pm)
        widget.quantity = 300
        widget.decrease_value()
        widget.decrease_value()
        assert widget.quantity == 100
        assert pm.get_player_balance() == 300

    def test_decrease_value_when_not_allowed(self, qapp):
        # Verifies decrease is blocked when allow_click is False
        parent = QWidget()
        pm = PlayerManager()
        widget = ActionWidget(parent, player_manager=pm)
        widget.quantity = 200
        widget.allow_click = False
        widget.decrease_value()
        assert widget.quantity == 200

    def test_decrease_value_without_player_manager(self, qapp):
        # Tests that decrease fails gracefully without PlayerManager
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.quantity = 200
        widget.decrease_value()
        assert widget.quantity == 200


class TestActionWidgetDisplay:

    @patch('Game_code.action_manager.QPixmap')
    def test_set_pixmap(self, mock_pixmap, qapp):
        # Tests setting a QPixmap image on the widget
        parent = QWidget()
        widget = ActionWidget(parent)
        pixmap = QPixmap()
        widget.set_pixmap(pixmap)
        # Should set pixmap on image_label

    def test_hide_controls(self, qapp):
        # Verifies that hide_controls() hides plus and minus buttons
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.hide_controls()
        assert not widget.plus_btn.isVisible()
        assert not widget.minus_btn.isVisible()

    def test_show_controls_displays_buttons(self, qapp):
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.hide_controls()
        widget.show_controls()

        assert not widget.plus_btn.isHidden()
        assert not widget.minus_btn.isHidden()

    def test_show_controls_resets_quantity(self, qapp):
        # Ensures show_controls() resets quantity to 0
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.quantity = 500
        widget.show_controls()
        assert widget.quantity == 0

    def test_show_controls_resets_label(self, qapp):
        # Tests that show_controls() resets value label to "0"
        parent = QWidget()
        widget = ActionWidget(parent)
        widget.quantity = 500
        widget.show_controls()
        assert widget.value_label.text() == "0"


# ============================================================================
# NPCManager Tests (40 tests)
# ============================================================================

class TestNPCManagerInitialization:

    def test_npc_count(self, npc_manager):
        # Verifies that NPCManager initializes with exactly 5 NPCs
        assert len(npc_manager.npc_data_list) == 5

    def test_npc_data_is_list(self, npc_manager):
        # Checks that npc_data_list is a list structure
        assert isinstance(npc_manager.npc_data_list, list)

    def test_npc_names_correct(self, npc_manager):
        # Validates that all 5 NPC names are present (BORIS, WARIO, etc.)
        names = [npc["name"] for npc in npc_manager.npc_data_list]
        assert "BORIS" in names
        assert "WARIO" in names
        assert "ALBEDO" in names
        assert "GERALT" in names
        assert "JADWIDA" in names

    def test_all_npcs_have_name(self, npc_manager):
        # Ensures every NPC has a name field
        for npc in npc_manager.npc_data_list:
            assert "name" in npc

    def test_all_npcs_have_avatar(self, npc_manager):
        # Checks that every NPC has an avatar field
        for npc in npc_manager.npc_data_list:
            assert "avatar" in npc

    def test_all_npcs_have_dialogue(self, npc_manager):
        # Verifies every NPC has a dialogue field
        for npc in npc_manager.npc_data_list:
            assert "dialogue" in npc

    def test_npc_widgets_empty_initially(self, npc_manager):
        # Tests that npc_widgets list starts empty
        assert npc_manager.npc_widgets == []

    def test_selected_index_none_initially(self, npc_manager):
        # Ensures no NPC is selected on initialization
        assert npc_manager.selected_index is None

    def test_first_npc_is_boris(self, npc_manager):
        # Verifies that first NPC in list is BORIS
        assert npc_manager.npc_data_list[0]["name"] == "BORIS"

    def test_second_npc_is_wario(self, npc_manager):
        # Checks that second NPC in list is WARIO
        assert npc_manager.npc_data_list[1]["name"] == "WARIO"


class TestNPCManagerDataAccess:

    def test_get_npc_data_valid_index(self, npc_manager):
        # Tests retrieving NPC data using a valid index
        npc_data = npc_manager.get_npc_data(0)
        assert npc_data["name"] == "BORIS"

    def test_get_npc_data_last_index(self, npc_manager):
        # Verifies getting last NPC data (index 4)
        npc_data = npc_manager.get_npc_data(4)
        assert npc_data["name"] == "JADWIDA"

    def test_get_npc_data_negative_index(self, npc_manager):
        # Checks that negative index returns None
        assert npc_manager.get_npc_data(-1) is None

    def test_get_npc_data_too_large_index(self, npc_manager):
        # Tests that out-of-range index returns None
        assert npc_manager.get_npc_data(10) is None

    def test_get_npc_data_boundary_valid(self, npc_manager):
        # Validates boundary case for maximum valid index (4)
        npc_data = npc_manager.get_npc_data(4)
        assert npc_data is not None

    def test_get_npc_data_boundary_invalid(self, npc_manager):
        # Tests boundary case for first invalid index (5)
        assert npc_manager.get_npc_data(5) is None

    def test_get_selected_npc_data_none_selected(self, npc_manager):
        # Verifies None is returned when no NPC is selected
        assert npc_manager.get_selected_npc_data() is None

    def test_get_selected_npc_data_after_selection(self, npc_manager, qapp):
        # Tests getting data of currently selected NPC
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(0)
        selected = npc_manager.get_selected_npc_data()
        assert selected["name"] == "BORIS"


class TestNPCManagerWidgetCreation:

    def test_create_npc_widgets_returns_list(self, npc_manager, qapp):
        # Checks that create_npc_widgets returns a list
        parent = QWidget()
        widgets = npc_manager.create_npc_widgets(parent)
        assert isinstance(widgets, list)

    def test_create_npc_widgets_correct_count(self, npc_manager, qapp):
        # Verifies exactly 5 NPC widgets are created
        parent = QWidget()
        widgets = npc_manager.create_npc_widgets(parent)
        assert len(widgets) == 5

    def test_create_npc_widgets_stores_references(self, npc_manager, qapp):
        # Tests that widgets are stored in npc_widgets list
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        assert len(npc_manager.npc_widgets) == 5

    def test_npc_widgets_are_npc_widget_instances(self, npc_manager, qapp):
        # Ensures created widgets are NPCWidget instances
        parent = QWidget()
        widgets = npc_manager.create_npc_widgets(parent)
        for widget in widgets:
            assert isinstance(widget, NPCWidget)


class TestNPCManagerSelection:

    def test_on_npc_clicked_sets_selected_index(self, npc_manager, qapp):
        # Tests that clicking an NPC sets the selected_index
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(2)
        assert npc_manager.selected_index == 2

    def test_on_npc_clicked_unselects_previous(self, npc_manager, qapp):
        # Verifies clicking new NPC unselects previously selected one
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(0)
        npc_manager.on_npc_clicked(1)
        assert npc_manager.selected_index == 1

    def test_on_npc_clicked_marks_widget_selected(self, npc_manager, qapp):
        # Checks that clicked widget is marked as selected
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(0)
        assert npc_manager.npc_widgets[0].is_selected

    def test_on_npc_clicked_unmarks_previous_widget(self, npc_manager, qapp):
        # Ensures previous widget is unmarked when selecting new one
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(0)
        npc_manager.on_npc_clicked(1)
        assert not npc_manager.npc_widgets[0].is_selected

    def test_unselect_npc_clears_index(self, npc_manager, qapp):
        # Tests that unselect_npc() clears selected_index to None
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.selected_index = 2
        npc_manager.unselect_npc()
        assert npc_manager.selected_index is None

    def test_unselect_npc_unmarks_widget(self, npc_manager, qapp):
        # Verifies unselect_npc() unmarks the widget
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.on_npc_clicked(0)
        npc_manager.unselect_npc()
        assert not npc_manager.npc_widgets[0].is_selected

    def test_unselect_when_none_selected(self, npc_manager, qapp):
        # Checks that unselecting when nothing is selected doesn't error
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.unselect_npc()  # Should not raise


class TestNPCManagerDialogUpdate:

    @patch('Game_code.npc_manager.ask_bot', return_value='AI response')
    def test_update_dialog_ai_calls_ask_bot(self, mock_ask_bot, npc_manager, qapp):
        # Tests that update_dialog_ai() calls the AI ask_bot function
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.update_dialog_ai(0)
        assert mock_ask_bot.called

    @patch('Game_code.npc_manager.ask_bot', return_value='AI response')
    def test_update_dialog_ai_updates_data(self, mock_ask_bot, npc_manager, qapp):
        # Verifies AI response is stored in NPC's dialogue data
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.update_dialog_ai(0)
        assert 'AI response' in npc_manager.npc_data_list[0]['dialogue']

    @patch('Game_code.npc_manager.ask_bot', return_value='Line1\nLine2')
    def test_update_dialog_ai_formats_multiline(self, mock_ask_bot, npc_manager, qapp):
        # Checks that multiline responses are formatted with <br> tags
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.update_dialog_ai(0)
        assert '<br>' in npc_manager.npc_data_list[0]['dialogue']

    @patch('Game_code.npc_manager.ask_bot', return_value='Test')
    def test_update_dialog_ai_invalid_index(self, mock_ask_bot, npc_manager, qapp):
        # Tests that invalid index doesn't crash the update
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)
        npc_manager.update_dialog_ai(10)  # Should not crash


# ============================================================================
# Stock Data Tests (30 tests)
# ============================================================================

class TestStockDataDates:

    def test_get_turn_dates_turn_0(self):
        # Verifies turn 0 returns dates: 2015-01-01 to 2015-02-28
        start, end = get_turn_dates(0)
        assert start == "2015-01-01"
        assert end == "2015-02-28"

    def test_get_turn_dates_turn_1(self):
        # Tests turn 1 dates (3 months later)
        start, end = get_turn_dates(1)
        assert start == "2015-04-01"
        assert end == "2015-05-28"

    def test_get_turn_dates_turn_2(self):
        # Tests turn 2 dates (6 months from start)
        start, end = get_turn_dates(2)
        assert start == "2015-07-01"
        assert end == "2015-08-28"

    def test_get_turn_dates_turn_5(self):
        # Verifies turn 5 dates calculation
        start, end = get_turn_dates(5)
        assert start == "2016-04-01"
        assert end == "2016-05-28"

    def test_get_turn_dates_turn_10(self):
        # Tests turn 10 dates (30 months from start)
        start, end = get_turn_dates(10)
        assert start == "2017-07-01"
        assert end == "2017-08-28"

    def test_get_turn_dates_returns_strings(self):
        # Checks that dates are returned as string type
        start, end = get_turn_dates(0)
        assert isinstance(start, str)
        assert isinstance(end, str)

    def test_get_turn_dates_format(self):
        # Validates date format is YYYY-MM-DD
        start, end = get_turn_dates(0)
        assert len(start) == 10
        assert start[4] == '-'
        assert start[7] == '-'


class TestStockDataPriceChange:

    def test_get_price_change_nonexistent_file(self):
        # Tests that non-existent CSV returns 1.0 (no change)
        result = get_price_change("NONEXISTENT123")
        assert result == 1.0

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,100\n2024-01-02,150\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_increase(self, mock_exists, mock_file):
        # Verifies price increase calculation (100 to 150 = 1.5)
        result = get_price_change("TEST")
        assert result == 1.5

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,200\n2024-01-02,100\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_decrease(self, mock_exists, mock_file):
        # Tests price decrease calculation (200 to 100 = 0.5)
        result = get_price_change("TEST")
        assert result == 0.5

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,100\n2024-01-02,100\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_no_change(self, mock_exists, mock_file):
        # Checks that same price returns 1.0
        result = get_price_change("TEST")
        assert result == 1.0

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,0\n2024-01-02,100\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_zero_start(self, mock_exists, mock_file):
        # Tests that zero start price returns 1.0 (avoid division by zero)
        result = get_price_change("TEST")
        assert result == 1.0  # Avoid division by zero

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_empty_data(self, mock_exists, mock_file):
        # Verifies empty CSV returns 1.0
        result = get_price_change("TEST")
        assert result == 1.0

    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,100\n')
    @patch('os.path.exists', return_value=True)
    def test_get_price_change_single_price(self, mock_exists, mock_file):
        # Tests that single price point returns 1.0
        result = get_price_change("TEST")
        assert result == 1.0


class TestStockDataFileOperations:

    @patch('glob.glob')
    @patch('os.remove')
    def test_clear_stock_files_csv(self, mock_remove, mock_glob):
        # Tests clearing CSV files from Stock_prizes folder
        mock_glob.side_effect = [
            ['file1.csv', 'file2.csv'],
            []
        ]
        clear_stock_files()
        assert mock_remove.call_count == 2

    @patch('glob.glob')
    @patch('os.remove')
    def test_clear_stock_files_charts(self, mock_remove, mock_glob):
        # Verifies clearing chart PNG files from Stock_charts folder
        mock_glob.side_effect = [
            [],
            ['chart1.png', 'chart2.png']
        ]
        clear_stock_files()
        assert mock_remove.call_count == 2

    @patch('glob.glob')
    @patch('os.remove')
    def test_clear_stock_files_both(self, mock_remove, mock_glob):
        # Tests clearing both CSV and chart files
        mock_glob.side_effect = [
            ['file1.csv'],
            ['chart1.png']
        ]
        clear_stock_files()
        assert mock_remove.call_count == 2

    @patch('glob.glob', return_value=[])
    @patch('os.remove')
    def test_clear_stock_files_empty(self, mock_remove, mock_glob):
        # Checks that clearing when no files exist doesn't error
        clear_stock_files()
        assert not mock_remove.called

    @patch('glob.glob')
    @patch('os.remove', side_effect=OSError)
    def test_clear_stock_files_handles_errors(self, mock_remove, mock_glob):
        # Verifies that OS errors during file deletion are handled gracefully
        mock_glob.side_effect = [['file1.csv'], ['chart1.png']]
        clear_stock_files()  # Should not raise


class TestStockDataGeneration:

    @patch('Game_code.stock_data.yf.Ticker')
    def test_get_data_calls_yfinance(self, mock_ticker):
        # Tests that get_data() calls yfinance API to fetch stock data
        mock_instance = Mock()
        mock_instance.history.return_value = Mock()
        mock_instance.history.return_value.to_csv = Mock()
        mock_ticker.return_value = mock_instance

        get_data(["AAPL"], 0)
        assert mock_ticker.called

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.plot')
    @patch('builtins.open', new_callable=mock_open, read_data='Date,Close\n2024-01-01,100\n2024-01-02,105\n')
    @patch('os.path.exists', return_value=True)
    def test_get_data_chart_creates_chart(self, mock_exists, mock_file, mock_plot, mock_savefig):
        # Verifies that get_data_chart() creates and saves a chart image
        get_data_chart("AAPL")
        assert mock_savefig.called

    @patch('os.path.exists', return_value=False)
    def test_get_data_chart_missing_csv(self, mock_exists):
        # Tests that missing CSV doesn't crash chart generation
        get_data_chart("NONEXISTENT")  # Should not crash


# ============================================================================
# ClickableLabel Tests (10 tests)
# ============================================================================

class TestClickableLabel:

    def test_clickable_label_creation(self, qapp):
        # Tests creating a ClickableLabel widget
        parent = QWidget()
        label = ClickableLabel(parent)
        assert label is not None

    def test_clickable_label_has_signal(self, qapp):
        # Verifies ClickableLabel has a clicked signal
        parent = QWidget()
        label = ClickableLabel(parent)
        assert hasattr(label, 'clicked')

    def test_clickable_label_emits_on_click(self, qapp, qtbot):
        # Tests that clicking emits the clicked signal
        parent = QWidget()
        label = ClickableLabel(parent)
        label.show()

        # Use a simpler approach - connect to a slot and verify it's called
        clicked = False
        def on_clicked():
            nonlocal clicked
            clicked = True

        label.clicked.connect(on_clicked)

        # Simulate mouse press with updated constructor
        from PySide6.QtCore import QPoint, QPointF
        from PySide6.QtGui import QMouseEvent
        from PySide6.QtCore import QEvent

        # Use the non-deprecated constructor
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(10.0, 10.0),  # Use QPointF instead of QPoint
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        label.mousePressEvent(event)

        assert clicked

    def test_clickable_label_text(self, qapp):
        # Checks that text can be set and retrieved on ClickableLabel
        parent = QWidget()
        label = ClickableLabel(parent)
        label.setText("Test")
        assert label.text() == "Test"


# ============================================================================
# NPCWidget Tests (10 tests)
# ============================================================================

class TestNPCWidget:

    def test_npc_widget_creation(self, qapp):
        # Tests creating an NPCWidget with NPC data
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert widget is not None

    def test_npc_widget_stores_index(self, qapp):
        # Verifies widget stores its index correctly
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 3, parent)
        assert widget.index == 3

    def test_npc_widget_stores_data(self, qapp):
        # Checks that widget stores NPC data reference
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert widget.npc_data == npc_data

    def test_npc_widget_not_selected_initially(self, qapp):
        # Ensures widget is not selected on creation
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert not widget.is_selected

    def test_npc_widget_set_selected_true(self, qapp):
        # Tests setting widget as selected
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        widget.set_selected(True)
        assert widget.is_selected

    def test_npc_widget_set_selected_false(self, qapp):
        # Verifies unsetting widget selection
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        widget.set_selected(True)
        widget.set_selected(False)
        assert not widget.is_selected

    def test_npc_widget_has_avatar_label(self, qapp):
        # Checks widget has avatar_image label component
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert hasattr(widget, 'avatar_image')

    def test_npc_widget_has_nickname_label(self, qapp):
        # Ensures widget has nickname_label component
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert hasattr(widget, 'nickname_label')

    def test_npc_widget_has_dialogue_label(self, qapp):
        # Verifies widget has dialogue_label component
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert hasattr(widget, 'dialogue_label')

    def test_npc_widget_dialogue_hidden_initially(self, qapp):
        # Tests that dialogue label is hidden by default
        parent = QWidget()
        npc_data = {"name": "TEST", "avatar": "test.png", "dialogue": "Test dialogue"}
        widget = NPCWidget(npc_data, 0, parent)
        assert not widget.dialogue_label.isVisible()


# ============================================================================
# Integration Tests (20 tests)
# ============================================================================

class TestIntegrationPlayerAction:

    def test_buy_stock_reduces_balance(self, qapp):
        # Tests that buying stock (increase_value) reduces player balance
        pm = PlayerManager()
        pm.set_player_balance(1000)
        parent = QWidget()
        balance_label = QLabel()

        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.increase_value()

        assert pm.get_player_balance() == 900

    def test_sell_stock_increases_balance(self, qapp):
        # Verifies selling stock (decrease_value) increases player balance
        pm = PlayerManager()
        pm.set_player_balance(1000)
        parent = QWidget()
        balance_label = QLabel()

        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.quantity = 100
        widget.decrease_value()

        assert pm.get_player_balance() == 1100

    def test_multiple_transactions(self, qapp):
        # Tests multiple buy and sell transactions update balance correctly
        pm = PlayerManager()
        pm.set_player_balance(1000)
        parent = QWidget()
        balance_label = QLabel()

        widget = ActionWidget(parent, player_manager=pm, balance_label=balance_label)
        widget.increase_value()  # 900
        widget.increase_value()  # 800
        widget.decrease_value()  # 900

        assert pm.get_player_balance() == 900

    def test_cannot_buy_with_insufficient_funds(self, qapp):
        # Ensures buying is blocked when balance is too low
        pm = PlayerManager()
        pm.set_player_balance(50)
        parent = QWidget()

        widget = ActionWidget(parent, player_manager=pm)
        widget.increase_value()

        assert widget.quantity == 0
        assert pm.get_player_balance() == 50


class TestIntegrationActionManager:

    def test_randomize_selects_six_stocks(self, action_manager, qapp):
        # Tests that randomize_actions() selects exactly 6 stocks
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        action_manager.randomize_actions()

        assert action_manager.all_actions_selected()

    def test_randomize_unique_selections(self, action_manager, qapp):
        # Verifies randomize creates 6 unique selections (no duplicates)
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        action_manager.randomize_actions()

        selections = action_manager.selected_actions
        assert len(set(selections)) == 6

    def test_reset_after_selection(self, action_manager, qapp):
        # Tests that reset_selections() clears all after randomizing
        parent = QWidget()
        action_manager.create_action_widgets(parent)
        action_manager.randomize_actions()
        action_manager.reset_selections()

        assert not action_manager.all_actions_selected()

    def test_widget_quantity_reset_on_reset(self, action_manager, qapp):
        # Checks that widget quantities are reset to 0 on reset
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(1000)
        widgets = action_manager.create_action_widgets(parent, player_manager=pm)

        widgets[0].increase_value()
        action_manager.reset_selections()

        assert widgets[0].quantity == 0


class TestIntegrationNPCSelection:

    def test_select_different_npcs(self, npc_manager, qapp):
        # Tests selecting different NPCs updates selection correctly
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.on_npc_clicked(0)
        first_selection = npc_manager.get_selected_npc_data()

        npc_manager.on_npc_clicked(1)
        second_selection = npc_manager.get_selected_npc_data()

        assert first_selection["name"] != second_selection["name"]

    def test_only_one_npc_selected_at_time(self, npc_manager, qapp):
        # Verifies only one NPC can be selected at a time
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.on_npc_clicked(0)
        npc_manager.on_npc_clicked(1)

        assert not npc_manager.npc_widgets[0].is_selected
        assert npc_manager.npc_widgets[1].is_selected


class TestIntegrationStockUpdates:

    @patch('Game_code.action_manager.get_price_change', return_value=1.5)
    def test_update_values_increases_investment(self, mock_price, action_manager, qapp):
        # Tests that positive price change increases investment value
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(1000)
        widgets = action_manager.create_action_widgets(parent, player_manager=pm)

        action_manager.selected_actions[0] = "AAPL"
        widgets[0].quantity = 100

        action_manager.update_value_labels_by_stock()

        assert widgets[0].quantity == 150

    @patch('Game_code.action_manager.get_price_change', return_value=0.5)
    def test_update_values_decreases_investment(self, mock_price, action_manager, qapp):
        # Verifies negative price change decreases investment value
        parent = QWidget()
        pm = PlayerManager()
        pm.set_player_balance(1000)
        widgets = action_manager.create_action_widgets(parent, player_manager=pm)

        action_manager.selected_actions[0] = "AAPL"
        widgets[0].quantity = 100

        action_manager.update_value_labels_by_stock()

        assert widgets[0].quantity == 50


class TestEdgeCases:

    def test_player_zero_balance_transactions(self, qapp):
        # Tests that transactions fail appropriately with zero balance
        pm = PlayerManager()
        pm.set_player_balance(0)
        parent = QWidget()
        widget = ActionWidget(parent, player_manager=pm)

        widget.increase_value()
        assert widget.quantity == 0

    def test_action_manager_no_options(self):
        # Verifies ActionManager works with empty options dictionary
        am = ActionManager()
        for stock in list(am.options.keys()):
            am.remove_option(stock)

        assert len(am.get_available_options()) == 0

    def test_npc_manager_empty_dialogue(self, npc_manager):
        # Tests NPC with empty dialogue string
        npc_manager.npc_data_list[0]['dialogue'] = ""
        assert npc_manager.npc_data_list[0]['dialogue'] == ""

    def test_very_large_stock_quantity(self, qapp):
        # Checks handling of very large investment quantities (10,000)
        pm = PlayerManager()
        pm.set_player_balance(1000000)
        parent = QWidget()
        widget = ActionWidget(parent, player_manager=pm)

        for _ in range(100):
            widget.increase_value()

        assert widget.quantity == 10000

    def test_negative_balance_after_loss(self, qapp):
        # Verifies that negative balances are allowed
        pm = PlayerManager()
        pm.set_player_balance(-500)
        assert pm.get_player_balance() == -500


# ============================================================================
# Run all tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--maxfail=5"])
