import pytest
from unittest.mock import patch, MagicMock
from game.AI import ask_bot

@patch("AI.client")
def test_ask_bot_returns_string(mock_client):
    mock_response = MagicMock()
    mock_response.output_text = "Test response"
    mock_client.responses.create.return_value = mock_response

    result = ask_bot(custom_question="Hello", personality_name="WARIO")
    assert result == "Test response"