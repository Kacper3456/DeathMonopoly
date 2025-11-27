import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game.action_manager import ActionManager, ActionWidget
from unittest.mock import Mock

def test_create_widgets():
    am = ActionManager()
    widgets = am.create_action_widgets(parent=None)
    assert len(widgets) == 6
    for w in widgets:
        assert isinstance(w, ActionWidget)

def test_randomize_actions_sets_selections():
    am = ActionManager()
    am.create_action_widgets(parent=None)
    am.randomize_actions()
    selected = am.get_selected_actions()
    assert all(a is not None for a in selected)

def test_all_actions_selected():
    am = ActionManager()
    am.selected_actions = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA"]
    assert am.all_actions_selected() is True
    am.selected_actions[0] = None
    assert am.all_actions_selected() is False


def test_reset_selections(setup_game):
    _, action_manager, _ = setup_game
    action_manager.randomize_actions()
    assert action_manager.all_actions_selected()

    action_manager.reset_selections()
    assert action_manager.get_missing_count() == 6
    for widget in action_manager.action_widgets:
        assert widget.quantity == 0
        assert widget.value_label.text() == "0"


def test_increase_decrease_without_balance(setup_game):
    player_manager, action_manager, _ = setup_game
    widget = action_manager.action_widgets[0]

    # Ustaw balance na 0
    player_manager.set_player_balance(0)
    widget.increase_value()
    assert widget.quantity == 0
    assert player_manager.get_player_balance() == 0