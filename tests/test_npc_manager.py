import pytest
from game.npc_manager import NPCManager
from unittest.mock import patch


def test_create_npcs():
    manager = NPCManager()
    widgets = manager.create_npc_widgets(parent_widget=None)
    assert len(widgets) == len(manager.npc_data_list)

def test_get_npc_data():
    manager = NPCManager()
    data = manager.get_npc_data(0)
    assert "name" in data
    assert "avatar" in data

def test_npc_selection(setup_game):
    _, _, npc_manager = setup_game

    npc_manager.on_npc_clicked(2)
    assert npc_manager.selected_index == 2
    for i, npc in enumerate(npc_manager.npc_widgets):
        if i == 2:
            assert npc.is_selected
        else:
            assert not npc.is_selected

def test_update_dialog_ai_calls_ai(setup_game):
    _, action_manager, npc_manager = setup_game

    with patch("game.AI.ask_bot") as mock_ask_bot:
        mock_ask_bot.return_value = "AI RESPONSE"
        npc_manager.update_dialog_ai(index=1, player_balance=5000, selected_companies=["AAPL", "GOOG"])
        assert npc_manager.npc_widgets[1].dialogue_label.text() == "AI RESPONSE"