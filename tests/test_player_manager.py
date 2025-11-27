import pytest
from game.player_manager import PlayerManager

def test_initial_balance():
    pm = PlayerManager()
    assert pm.get_player_balance() == 10000

def test_set_balance():
    pm = PlayerManager()
    pm.set_player_balance(5000)
    assert pm.get_player_balance() == 5000

def test_update_player_data():
    pm = PlayerManager()
    pm.update_player_data(name="Alice", avatar="avatar.png", dialogue="Hello")
    data = pm.get_player_data()
    assert data["name"] == "Alice"
    assert data["avatar"] == "avatar.png"
    assert data["dialogue"] == "Hello"