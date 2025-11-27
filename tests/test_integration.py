import pytest
from unittest.mock import patch, MagicMock
from game.player_manager import PlayerManager
from game.action_manager import ActionManager
from game.npc_manager import NPCManager
from game.stock_data import get_price_change


# --- FIXTURE: SETUP ---
@pytest.fixture
def setup_game():
    player_manager = PlayerManager()
    action_manager = ActionManager()
    npc_manager = NPCManager()

    # Tworzymy "widgety" (tu same obiekty logiczne, nie GUI)
    action_manager.create_action_widgets(parent=None, player_manager=player_manager, balance_label=None)
    npc_manager.create_npc_widgets(parent_widget=None)

    return player_manager, action_manager, npc_manager


# --- TEST 1: GRACZ ZAKUPUJE AKCJE ---
def test_player_investment_updates_balance(setup_game):
    player_manager, action_manager, _ = setup_game

    widget = action_manager.action_widgets[0]
    initial_balance = player_manager.get_player_balance()

    # Symulujemy kliknięcie "+"
    widget.increase_value()
    widget.increase_value()  # +200

    assert widget.quantity == 200
    assert player_manager.get_player_balance() == initial_balance - 200

    # Symulujemy kliknięcie "-"
    widget.decrease_value()
    assert widget.quantity == 100
    assert player_manager.get_player_balance() == initial_balance - 100


# --- TEST 2: LOSOWANIE AKCJI I AKTUALIZACJA WYKRESÓW ---
def test_randomize_actions_and_charts(setup_game):
    _, action_manager, _ = setup_game

    action_manager.randomize_actions()
    selected = action_manager.get_selected_actions()
    assert all(selected)  # wszystkie akcje wybrane

    # Mockujemy get_price_change dla testu
    with patch("action_manager.get_price_change", return_value=1.5):
        action_manager.update_value_labels_by_stock()
        for widget in action_manager.action_widgets:
            assert widget.quantity == 150 if widget.quantity != 0 else 0


# --- TEST 3: NPC REAGUJE NA WYBORY GRACZA ---
@patch("AI.ask_bot")
def test_npc_dialogue_update(mock_ask_bot, setup_game):
    player_manager, action_manager, npc_manager = setup_game

    # Symulujemy inwestycję
    widget = action_manager.action_widgets[0]
    widget.quantity = 100

    action_manager.selected_actions[0] = "AAPL"

    # Mockujemy AI
    mock_ask_bot.return_value = "Congrats, your investment in AAPL did well!"

    npc_manager.update_dialog_ai(
        index=0,
        player_balance=player_manager.get_player_balance(),
        selected_companies=action_manager.get_selected_actions()
    )

    dialogue = npc_manager.npc_widgets[0].dialogue_label.text()
    assert "Congrats" in dialogue


# --- TEST 4: SPRAWDZENIE BRAKU WYBRANYCH AKCJI ---
def test_missing_actions(setup_game):
    _, action_manager, _ = setup_game
    action_manager.reset_selections()
    assert action_manager.get_missing_count() == 6
    assert not action_manager.all_actions_selected()