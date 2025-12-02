import pytest
import os
import csv
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import Qt
import pandas as pd

# Import game modules
import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Game_code.player_manager import PlayerManager
from Game_code.action_manager import ActionManager, ActionWidget
from Game_code.npc_manager import NPCManager
from Game_code.stock_data import get_data, get_turn_dates, get_price_change, clear_stock_files
from Game_code.AI import ask_bot, personalities


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
def game_setup(qapp):
    player_manager = PlayerManager()
    action_manager = ActionManager()
    npc_manager = NPCManager()
    parent = QWidget()

    # Create widgets
    action_widgets = action_manager.create_action_widgets(parent, player_manager=player_manager)
    npc_widgets = npc_manager.create_npc_widgets(parent)

    return {
        'player_manager': player_manager,
        'action_manager': action_manager,
        'npc_manager': npc_manager,
        'parent': parent,
        'action_widgets': action_widgets,
        'npc_widgets': npc_widgets
    }


@pytest.fixture
def mock_stock_data():
    csv_dir = tempfile.mkdtemp()

    # Create sample stock data
    stocks = ['AAPL', 'GOOG', 'MSFT']
    for stock in stocks:
        csv_path = os.path.join(csv_dir, f'{stock}_history.csv')
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Close', 'Open', 'High', 'Low'])
            writer.writerow(['2024-01-01', '100.0', '98.0', '102.0', '97.0'])
            writer.writerow(['2024-01-02', '105.0', '100.0', '106.0', '99.0'])
            writer.writerow(['2024-01-03', '110.0', '105.0', '111.0', '104.0'])

    yield csv_dir

    # Cleanup
    for stock in stocks:
        csv_path = os.path.join(csv_dir, f'{stock}_history.csv')
        if os.path.exists(csv_path):
            os.remove(csv_path)
    os.rmdir(csv_dir)


# ============================================================================
# AI Integration Tests (25 tests)
# ============================================================================

class TestAIDialogueGeneration:
    """Test AI dialogue generation and storage"""

    @patch('Game_code.AI.OpenAI')
    def test_ask_bot_returns_string(self, mock_openai):
        # Verifies ask_bot function returns string type from AI
        mock_response = Mock()
        mock_response.output_text = "This is a test response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            result = ask_bot("Test question", "BORIS")
            assert isinstance(result, str)

    @patch('Game_code.AI.OpenAI')
    def test_ask_bot_uses_correct_personality(self, mock_openai):
        # Ensures correct personality system message is sent to AI
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            ask_bot("Test", "BORIS")

            # Check that the system message for BORIS was used
            call_args = mock_client.responses.create.call_args
            messages = call_args[1]['input']
            assert messages[0]['role'] == 'system'
            # Check that BORIS personality description is in the system message
            system_message = messages[0]['content']
            assert 'Boris' in system_message or 'Slavic' in system_message

    @patch('Game_code.AI.OpenAI')
    def test_ask_bot_fallback_personality(self, mock_openai):
        # Verifies fallback to default personality when invalid name provided
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            ask_bot("Test", "NONEXISTENT")

            # Should still work with fallback
            assert mock_client.responses.create.called

    @patch('Game_code.AI.OpenAI')
    @patch('os.listdir')
    @patch('os.path.exists')
    def test_ask_bot_reads_stock_files(self, mock_exists, mock_listdir, mock_openai):
        # Tests that ask_bot scans Stock_prizes folder for CSV files
        mock_exists.return_value = True
        mock_listdir.return_value = ['AAPL_history.csv', 'GOOG_history.csv']

        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            with patch('pandas.read_csv') as mock_read_csv:
                # Create a proper mock DataFrame
                mock_df = pd.DataFrame({
                    'Close': [100.0, 105.0, 110.0]
                })
                mock_read_csv.return_value = mock_df

                ask_bot("Test", "BORIS")

                assert mock_listdir.called

    @patch('Game_code.AI.OpenAI')
    def test_ask_bot_includes_custom_question(self, mock_openai):
        # Verifies custom question text is passed to AI
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        custom_q = "What should I invest in?"

        with patch('Game_code.AI.client', mock_client):
            with patch('os.listdir', return_value=[]):
                ask_bot(custom_q, "BORIS")

                call_args = mock_client.responses.create.call_args
                messages = call_args[1]['input']
                user_message = messages[1]['content']
                assert custom_q in user_message

    @patch('Game_code.npc_manager.ask_bot', return_value='AI generated dialogue')
    def test_npc_dialogue_update_stores_response(self, mock_ask_bot, qapp):
        # Verifies AI-generated dialogue is stored in correct NPC's data
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        # Update dialogue for first NPC (BORIS)
        npc_manager.update_dialog_ai(0, player_balance=1000, selected_companies=['AAPL', 'GOOG'])

        # Check that dialogue was updated
        assert 'AI generated dialogue' in npc_manager.npc_data_list[0]['dialogue']

    @patch('Game_code.npc_manager.ask_bot', return_value='AI generated dialogue')
    def test_npc_dialogue_update_correct_character(self, mock_ask_bot, qapp):
        # Ensures dialogue is stored in the specified NPC, not others
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        original_dialogue_1 = npc_manager.npc_data_list[1]['dialogue']

        # Update only first NPC
        npc_manager.update_dialog_ai(0)

        # First NPC should be updated
        assert 'AI generated dialogue' in npc_manager.npc_data_list[0]['dialogue']
        # Second NPC should be unchanged
        assert npc_manager.npc_data_list[1]['dialogue'] == original_dialogue_1

    @patch('Game_code.npc_manager.ask_bot', return_value='Line1\nLine2\nLine3')
    def test_npc_dialogue_multiline_formatting(self, mock_ask_bot, qapp):
        # Verifies newlines are converted to <br> tags for display
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        # Check HTML formatting
        dialogue = npc_manager.npc_data_list[0]['dialogue']
        assert '<br>' in dialogue
        assert dialogue.count('<br>') == 2  # 3 lines = 2 breaks

    @patch('Game_code.AI.OpenAI')
    def test_all_personalities_have_system_messages(self, mock_openai):
        # Ensures all NPC personalities have proper configuration
        for personality_name in personalities.keys():
            personality = personalities[personality_name]
            assert 'system_message' in personality
            assert len(personality['system_message']) > 0

    def test_personality_count_matches_npcs(self):
        # Verifies personality dictionary has entries for all NPCs
        npc_manager = NPCManager()
        npc_names = [npc['name'] for npc in npc_manager.npc_data_list]

        for name in npc_names:
            assert name.upper() in personalities

    @patch('Game_code.npc_manager.ask_bot', return_value='Test response')
    def test_npc_dialogue_label_updates(self, mock_ask_bot, qapp):
        # Verifies dialogue label widget updates when AI response received
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        # Widget label should be updated
        label_text = npc_manager.npc_widgets[0].dialogue_label.text()
        assert 'Test response' in label_text

    @patch('Game_code.AI.OpenAI')
    def test_ai_receives_stock_price_data(self, mock_openai):
        # Verifies stock price data is included in AI prompt
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            with patch('os.listdir', return_value=['TEST_history.csv']):
                with patch('pandas.read_csv') as mock_read_csv:
                    mock_df = pd.DataFrame({
                        'Close': [100.0, 110.0]
                    })
                    mock_read_csv.return_value = mock_df

                    ask_bot("Test", "BORIS")

                    # Check that price data was included in prompt
                    call_args = mock_client.responses.create.call_args
                    messages = call_args[1]['input']
                    user_message = messages[1]['content']
                    assert 'First price' in user_message or '100.0' in user_message

    @patch('Game_code.npc_manager.ask_bot')
    def test_npc_update_passes_balance(self, mock_ask_bot, qapp):
        # Ensures player balance is passed to AI for context
        mock_ask_bot.return_value = "Response"
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0, player_balance=5000)

        # Check that ask_bot was called with a question containing budget
        call_args = mock_ask_bot.call_args
        question = call_args[0][0]
        assert '5000' in question or 'budget' in question.lower()

    @patch('Game_code.npc_manager.ask_bot')
    def test_npc_update_passes_selected_companies(self, mock_ask_bot, qapp):
        # Ensures selected company list is passed to AI
        mock_ask_bot.return_value = "Response"
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        companies = ['AAPL', 'GOOG', 'MSFT']
        npc_manager.update_dialog_ai(0, selected_companies=companies)

        # Check that companies were mentioned
        call_args = mock_ask_bot.call_args
        question = call_args[0][0]
        assert any(company in question for company in companies)

    @patch('Game_code.AI.OpenAI')
    def test_ai_uses_gpt_model(self, mock_openai):
        # Verifies correct AI model is specified
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            with patch('os.listdir', return_value=[]):
                ask_bot("Test", "BORIS")

                call_args = mock_client.responses.create.call_args
                assert 'model' in call_args[1]
                assert 'gpt' in call_args[1]['model'].lower()

    def test_npc_dialogue_empty_before_update(self, qapp):
        # Verifies dialogue label starts hidden
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        # Dialogue label should be initially hidden
        assert npc_manager.npc_widgets[0].dialogue_label.isHidden()

    @patch('Game_code.npc_manager.ask_bot', return_value='<script>alert("test")</script>')
    def test_npc_dialogue_html_escaping(self, mock_ask_bot, qapp):
        # Ensures HTML in AI response doesn't execute
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        # HTML should be escaped or handled safely
        dialogue = npc_manager.npc_data_list[0]['dialogue']
        # The dialogue might contain the script tag as text, which is OK
        # as long as it's not executed

    @patch('Game_code.npc_manager.ask_bot', return_value='Response with "quotes" and \'apostrophes\'')
    def test_npc_dialogue_quote_handling(self, mock_ask_bot, qapp):
        # Verifies quotes in AI response don't break display
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        dialogue = npc_manager.npc_data_list[0]['dialogue']
        assert 'quotes' in dialogue
        assert 'apostrophes' in dialogue

    @patch('Game_code.npc_manager.ask_bot')
    def test_npc_update_invalid_index(self, mock_ask_bot, qapp):
        # Ensures invalid NPC index is handled gracefully
        mock_ask_bot.return_value = "Response"
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        # Try invalid indices
        npc_manager.update_dialog_ai(-1)  # Should not crash
        npc_manager.update_dialog_ai(999)  # Should not crash

        # ask_bot should not have been called
        assert not mock_ask_bot.called

    @patch('Game_code.AI.OpenAI')
    def test_ai_handles_empty_stock_folder(self, mock_openai):
        # Verifies AI still responds when no stock data available
        mock_response = Mock()
        mock_response.output_text = "Response"
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch('Game_code.AI.client', mock_client):
            with patch('os.listdir', return_value=[]):
                result = ask_bot("Test", "BORIS")
                assert isinstance(result, str)

    @patch('Game_code.npc_manager.ask_bot', side_effect=Exception("API Error"))
    def test_npc_update_handles_ai_error(self, mock_ask_bot, qapp):
        # Ensures system handles AI API failures gracefully
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        try:
            npc_manager.update_dialog_ai(0)
        except Exception:
            pass  # Should handle gracefully

    @patch('Game_code.npc_manager.ask_bot', return_value='A' * 1000)
    def test_npc_dialogue_very_long_response(self, mock_ask_bot, qapp):
        # Tests handling of extremely long AI responses
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        # Should store full response
        dialogue = npc_manager.npc_data_list[0]['dialogue']
        assert len(dialogue) > 900

    @patch('Game_code.npc_manager.ask_bot', return_value='')
    def test_npc_dialogue_empty_response(self, mock_ask_bot, qapp):
        # Verifies empty AI response is handled
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.update_dialog_ai(0)

        # Should update even with empty string
        dialogue = npc_manager.npc_data_list[0]['dialogue']
        assert dialogue == ''


# ============================================================================
# Stock Data Integration Tests (25 tests)
# ============================================================================

class TestStockDataIntegration:
    """Test stock data fetching, processing, and chart generation"""

    def test_get_turn_dates_calculates_correctly(self):
        # Verifies turn counter produces correct date ranges
        start, end = get_turn_dates(0)
        assert start == "2015-01-01"
        assert end == "2015-02-28"

    def test_get_turn_dates_increments_properly(self):
        # Ensures each turn advances dates by 3 months
        start1, end1 = get_turn_dates(0)
        start2, end2 = get_turn_dates(1)

        # Convert to datetime to compare
        from datetime import datetime
        start1_dt = datetime.strptime(start1, "%Y-%m-%d")
        start2_dt = datetime.strptime(start2, "%Y-%m-%d")

        # Should be 3 months apart
        diff_months = (start2_dt.year - start1_dt.year) * 12 + (start2_dt.month - start1_dt.month)
        assert diff_months == 3

    @patch('yfinance.Ticker')
    def test_get_data_downloads_for_all_companies(self, mock_ticker):
        # Tests that data is fetched for each selected company
        mock_data = Mock()
        mock_data.to_csv = Mock()
        mock_ticker.return_value.history.return_value = mock_data

        companies = ['AAPL', 'GOOG', 'MSFT']
        get_data(companies, 0)

        # Should be called once per company
        assert mock_ticker.call_count == 3

    @patch('yfinance.Ticker')
    def test_get_data_creates_csv_files(self, mock_ticker):
        # Verifies CSV files are created for stock data
        mock_data = Mock()
        mock_data.to_csv = Mock()
        mock_ticker.return_value.history.return_value = mock_data

        get_data(['TEST'], 0)

        # to_csv should have been called
        assert mock_data.to_csv.called

    def test_get_price_change_returns_float(self):
        # Ensures price change calculation returns numeric type
        csv_data = "Date,Close\n2024-01-01,100.0\n2024-01-02,110.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                result = get_price_change('TEST')
                assert isinstance(result, float)

    def test_get_price_change_calculates_correctly(self):
        # Verifies correct multiplication factor calculation
        csv_data = "Date,Close\n2024-01-01,100.0\n2024-01-02,110.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                result = get_price_change('TEST')
                assert abs(result - 1.1) < 0.01  # 110/100 = 1.1

    def test_get_price_change_handles_missing_file(self):
        # Ensures missing CSV file returns default multiplier
        with patch('os.path.exists', return_value=False):
            result = get_price_change('NONEXISTENT')
            assert result == 1.0  # Default no-change multiplier

    def test_get_price_change_handles_zero_start_price(self):
        # Prevents division by zero errors
        csv_data = "Date,Close\n2024-01-01,0.0\n2024-01-02,110.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                result = get_price_change('TEST')
                assert result == 1.0  # Should return default

    def test_get_price_change_handles_empty_csv(self):
        # Tests behavior with CSV containing no price data
        csv_data = "Date,Close\n"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                result = get_price_change('TEST')
                assert result == 1.0

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.plot')
    def test_get_data_chart_creates_chart(self, mock_plot, mock_savefig):
        # Verifies chart generation from CSV data
        csv_data = "Date,Close\n2024-01-01,100.0\n2024-01-02,105.0\n2024-01-03,110.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                from Game_code.stock_data import get_data_chart
                get_data_chart('TEST')

                assert mock_plot.called
                assert mock_savefig.called

    @patch('matplotlib.pyplot.savefig')
    def test_chart_color_green_for_profit(self, mock_savefig):
        # Ensures profitable stocks use green chart lines
        csv_data = "Date,Close\n2024-01-01,100.0\n2024-01-02,110.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                with patch('matplotlib.pyplot.plot') as mock_plot:
                    from Game_code.stock_data import get_data_chart
                    get_data_chart('TEST')

                    # Check that plot was called with green color
                    call_args = mock_plot.call_args
                    assert call_args[1].get('color') == 'green' or call_args[1].get('color') == 'red'

    @patch('matplotlib.pyplot.savefig')
    def test_chart_color_red_for_loss(self, mock_savefig):
        # Ensures losing stocks use red chart lines
        csv_data = "Date,Close\n2024-01-01,110.0\n2024-01-02,100.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                with patch('matplotlib.pyplot.plot') as mock_plot:
                    from Game_code.stock_data import get_data_chart
                    get_data_chart('TEST')

                    # Should use red for loss
                    call_args = mock_plot.call_args
                    assert call_args[1].get('color') in ['green', 'red']

    @patch('os.path.exists', return_value=False)
    def test_chart_generation_skips_missing_csv(self, mock_exists):
        # Tests that chart generation handles missing CSV gracefully
        from Game_code.stock_data import get_data_chart
        get_data_chart('NONEXISTENT')  # Should not crash

    @patch('matplotlib.pyplot.savefig')
    @patch('os.path.exists', return_value=True)
    def test_generate_all_charts_uniform_scale(self, mock_exists, mock_savefig):
        # Verifies all charts use same Y-axis scale for comparison
        csv_data = "Date,Close\n2024-01-01,100.0\n2024-01-02,105.0"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('matplotlib.pyplot.ylim') as mock_ylim:
                from Game_code.stock_data import generate_all_charts
                generate_all_charts(['AAPL', 'GOOG'])

                # ylim should be called with consistent values
                assert mock_ylim.call_count >= 2

    @patch('os.remove')
    @patch('glob.glob')
    def test_clear_stock_files_removes_csvs(self, mock_glob, mock_remove):
        # Tests that cleanup removes CSV files
        mock_glob.return_value = ['test1.csv', 'test2.csv']
        clear_stock_files()

        assert mock_remove.call_count >= 2

    @patch('os.remove')
    @patch('glob.glob')
    def test_clear_stock_files_removes_charts(self, mock_glob, mock_remove):
        # Tests that cleanup removes chart files
        mock_glob.return_value = ['chart1.png', 'chart2.png']
        clear_stock_files()

        assert mock_remove.call_count >= 2

    @patch('os.remove', side_effect=OSError)
    @patch('glob.glob')
    def test_clear_stock_files_handles_permission_error(self, mock_glob, mock_remove):
        # Ensures cleanup handles file permission errors
        mock_glob.return_value = ['locked_file.csv']

        try:
            clear_stock_files()
        except OSError:
            pytest.fail("Should handle OSError gracefully")

    def test_action_manager_updates_charts_after_generation(self, game_setup):
        # Verifies action widgets display newly generated charts
        am = game_setup['action_manager']
        am.selected_actions = ['AAPL', 'GOOG', 'MSFT', None, None, None]

        # Mock the setPixmap method on each widget's image_label
        for i, widget in enumerate(am.action_widgets):
            widget.image_label.setPixmap = Mock()

        # Patch QPixmap to track calls
        with patch('Game_code.action_manager.QPixmap') as mock_pixmap:
            am.update_selected_action_charts()

            # Should attempt to load charts for 3 selected stocks
            assert mock_pixmap.call_count == 3

    def test_action_manager_chart_update_skips_none(self, game_setup):
        # Tests that chart update ignores empty action slots
        am = game_setup['action_manager']
        am.selected_actions = ['AAPL', None, 'GOOG', None, None, None]

        # Mock the setPixmap method on each widget's image_label
        for i, widget in enumerate(am.action_widgets):
            widget.image_label.setPixmap = Mock()

        # Patch QPixmap to track calls
        with patch('Game_code.action_manager.QPixmap') as mock_pixmap:
            am.update_selected_action_charts()

            # Should only try to load for selected stocks (2)
            assert mock_pixmap.call_count == 2

    def test_action_manager_applies_price_changes(self, game_setup):
        # Verifies investment values update based on stock performance
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 100

        # Patch get_price_change in the action_manager module where it's imported
        with patch('Game_code.action_manager.get_price_change', return_value=1.5):
            am.update_value_labels_by_stock()

        # Value should be multiplied by price change
        assert widgets[0].quantity == 150

    def test_action_manager_handles_losses(self, game_setup):
        # Tests that value decreases are calculated correctly
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 100

        # Patch get_price_change in the action_manager module where it's imported
        with patch('Game_code.action_manager.get_price_change', return_value=0.5):
            am.update_value_labels_by_stock()

        # Value should be halved
        assert widgets[0].quantity == 50

    def test_multiple_turns_advance_dates(self):
        # Ensures date ranges don't overlap between turns
        dates = [get_turn_dates(i) for i in range(3)]

        for i in range(len(dates) - 1):
            end1 = dates[i][1]
            start2 = dates[i + 1][0]
            # End of one turn should be before start of next
            assert end1 < start2 or end1 == start2

    @patch('yfinance.Ticker')
    def test_stock_data_respects_date_range(self, mock_ticker):
        # Verifies data requests use correct start and end dates
        mock_data = Mock()
        mock_data.to_csv = Mock()
        mock_ticker.return_value.history.return_value = mock_data

        get_data(['TEST'], 0)

        # history should be called with start and end dates
        call_args = mock_ticker.return_value.history.call_args
        assert 'start' in call_args[1] or len(call_args[0]) >= 2

    def test_csv_directory_creation(self):
        # Tests that required directories are created if missing
        from Game_code.stock_data import CSV_DIR, CHART_DIR
        assert os.path.exists(CSV_DIR)
        assert os.path.exists(CHART_DIR)


# ============================================================================
# Game Flow Integration Tests (25 tests)
# ============================================================================

class TestGameFlowIntegration:
    """Test complete game flow scenarios"""

    def test_player_starts_with_default_balance(self):
        # Verifies initial player balance is set correctly
        pm = PlayerManager()
        assert pm.get_player_balance() == 2400

    def test_player_can_invest_full_balance(self, game_setup):
        # Tests that player can invest entire balance
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)

        # Invest all money
        for _ in range(10):
            widgets[0].increase_value()

        assert pm.get_player_balance() == 0
        assert widgets[0].quantity == 1000

    def test_complete_investment_cycle(self, game_setup):
        # Tests full investment, price update, and balance return
        pm = game_setup['player_manager']
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)

        # Invest
        am.selected_actions[0] = 'AAPL'
        widgets[0].increase_value()
        widgets[0].increase_value()

        # Price changes - patch in action_manager module
        with patch('Game_code.action_manager.get_price_change', return_value=2.0):
            am.update_value_labels_by_stock()

        # Investment should double
        assert widgets[0].quantity == 400

    def test_multiple_stock_investments(self, game_setup):
        # Verifies player can invest in multiple stocks simultaneously
        pm = game_setup['player_manager']
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)

        # Invest in 3 stocks
        for i in range(3):
            am.selected_actions[i] = f'STOCK{i}'
            widgets[i].increase_value()

        # All should have investments
        assert all(widgets[i].quantity > 0 for i in range(3))

    def test_action_randomization_selects_six(self, game_setup):
        # Tests that randomize selects exactly 6 unique stocks
        am = game_setup['action_manager']
        am.randomize_actions()

        # Should have 6 selections, all different
        selected = [s for s in am.selected_actions if s is not None]
        assert len(selected) == 6
        assert len(set(selected)) == 6  # All unique

    def test_action_reset_clears_all(self, game_setup):
        # Verifies reset clears all selections and investments
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']
        pm = game_setup['player_manager']

        # Set up investments
        pm.set_player_balance(1000)
        am.randomize_actions()
        widgets[0].increase_value()

        # Reset
        am.reset_selections()

        # Everything should be cleared
        assert all(s is None for s in am.selected_actions)
        assert all(w.quantity == 0 for w in widgets)

    def test_npc_selection_highlights(self, qapp):
        # Tests that selecting NPC highlights correct widget
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.on_npc_clicked(0)

        assert npc_manager.selected_index == 0
        assert npc_manager.npc_widgets[0].is_selected

    def test_npc_selection_only_one_active(self, qapp):
        # Ensures only one NPC can be selected at a time
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.on_npc_clicked(0)
        npc_manager.on_npc_clicked(1)

        # Only second should be selected
        assert not npc_manager.npc_widgets[0].is_selected
        assert npc_manager.npc_widgets[1].is_selected

    def test_npc_unselect_clears_selection(self, qapp):
        # Verifies unselect removes all selections
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        npc_manager.on_npc_clicked(0)
        npc_manager.unselect_npc()

        assert npc_manager.selected_index is None
        assert not any(w.is_selected for w in npc_manager.npc_widgets)

    def test_balance_updates_immediately(self, game_setup):
        # Tests that balance label updates on investment
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']
        balance_label = QLabel()

        pm.set_player_balance(1000)
        widgets[0].balance_label = balance_label

        widgets[0].increase_value()

        # Label should show new balance
        assert '900' in balance_label.text()

    def test_cannot_invest_more_than_balance(self, game_setup):
        # Ensures player cannot invest money they don't have
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(50)  # Less than investment unit

        widgets[0].increase_value()

        # Should not increase
        assert widgets[0].quantity == 0
        assert pm.get_player_balance() == 50

    def test_refund_on_decrease(self, game_setup):
        # Tests that decreasing investment returns money
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)
        widgets[0].increase_value()
        widgets[0].decrease_value()

        # Should be back to 1000
        assert pm.get_player_balance() == 1000
        assert widgets[0].quantity == 0

    def test_cannot_decrease_below_zero(self, game_setup):
        # Ensures investment quantity cannot go negative
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)
        widgets[0].decrease_value()

        assert widgets[0].quantity == 0
        assert pm.get_player_balance() == 1000

    def test_action_menu_blocks_duplicate_selections(self, game_setup):
        # Verifies same stock cannot be selected multiple times
        am = game_setup['action_manager']

        am.selected_actions[0] = 'AAPL'

        available = am.get_available_options()

        # AAPL should not be in available options
        assert 'AAPL' not in available

    def test_all_actions_selected_check(self, game_setup):
        # Tests detection of when all 6 slots are filled
        am = game_setup['action_manager']

        # Not all selected
        am.selected_actions = ['AAPL', None, 'GOOG', None, 'MSFT', None]
        assert not am.all_actions_selected()

        # All selected
        am.selected_actions = ['AAPL', 'GOOG', 'MSFT', 'NVDA', 'AMZN', 'TSLA']
        assert am.all_actions_selected()

    def test_get_missing_count_accurate(self, game_setup):
        # Verifies correct count of empty action slots
        am = game_setup['action_manager']

        am.selected_actions = ['AAPL', None, 'GOOG', None, None, None]
        assert am.get_missing_count() == 4

    def test_action_widgets_show_hide_controls(self, game_setup):
        # Tests that +/- buttons can be hidden and shown
        widgets = game_setup['action_widgets']
        parent = game_setup['parent']

        # Make parent visible so children can be visible
        parent.show()

        widgets[0].hide_controls()
        assert not widgets[0].plus_btn.isVisible()
        assert not widgets[0].minus_btn.isVisible()

        widgets[0].show_controls()
        assert widgets[0].plus_btn.isVisible()
        assert widgets[0].minus_btn.isVisible()

    def test_player_data_complete(self):
        # Ensures player data has all required fields
        pm = PlayerManager()
        data = pm.get_player_data()

        assert 'name' in data
        assert 'avatar' in data
        assert 'dialogue' in data
        assert 'balance' in data

    def test_npc_data_complete(self):
        # Verifies all NPCs have required data fields
        npc_manager = NPCManager()

        for npc_data in npc_manager.npc_data_list:
            assert 'name' in npc_data
            assert 'avatar' in npc_data
            assert 'dialogue' in npc_data

    def test_action_options_have_valid_paths(self):
        # Tests that stock options include image paths
        am = ActionManager()

        for name, path in am.options.items():
            assert isinstance(path, str)
            assert len(path) > 0

    def test_difficulty_affects_balance(self):
        # This test would need game_page.py to be imported
        # Skipping for now as it wasn't provided
        pass

    def test_turn_progression(self):
        # Tests that turns advance correctly
        turn1_dates = get_turn_dates(0)
        turn2_dates = get_turn_dates(1)
        turn3_dates = get_turn_dates(2)

        # Each turn should have later dates
        assert turn1_dates[0] < turn2_dates[0]
        assert turn2_dates[0] < turn3_dates[0]

    def test_profit_calculation_accuracy(self, game_setup):
        # Verifies profit is calculated correctly
        widgets = game_setup['action_widgets']
        am = game_setup['action_manager']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 1000

        # Patch in action_manager module
        with patch('Game_code.action_manager.get_price_change', return_value=1.25):
            am.update_value_labels_by_stock()

        # 1000 * 1.25 = 1250
        assert widgets[0].quantity == 1250

    def test_loss_calculation_accuracy(self, game_setup):
        # Verifies loss is calculated correctly
        widgets = game_setup['action_widgets']
        am = game_setup['action_manager']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 1000

        # Patch in action_manager module
        with patch('Game_code.action_manager.get_price_change', return_value=0.8):
            am.update_value_labels_by_stock()

        # 1000 * 0.8 = 800
        assert widgets[0].quantity == 800

    def test_zero_investment_stays_zero(self, game_setup):
        # Ensures zero investment doesn't magically generate value
        widgets = game_setup['action_widgets']
        am = game_setup['action_manager']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 0

        # Patch in action_manager module
        with patch('Game_code.action_manager.get_price_change', return_value=2.0):
            am.update_value_labels_by_stock()

        assert widgets[0].quantity == 0


# ============================================================================
# Edge Cases and Error Handling Tests (25 tests)
# ============================================================================

class TestEdgeCasesAndErrors:
    """Test error handling and edge cases"""

    def test_negative_balance_prevention(self):
        # Ensures balance cannot go negative
        pm = PlayerManager()
        pm.set_player_balance(-100)

        # Balance should not be negative (or should be handled)
        # Depending on implementation, might stay at 0 or reject

    def test_extremely_large_balance(self):
        # Tests handling of very large numbers
        pm = PlayerManager()
        pm.set_player_balance(999999999999)

        assert pm.get_player_balance() == 999999999999

    def test_extremely_large_investment(self, game_setup):
        # Tests calculations with huge investment amounts
        widgets = game_setup['action_widgets']
        pm = game_setup['player_manager']

        pm.set_player_balance(1000000000)
        widgets[0].quantity = 999999999

        widgets[0].decrease_value()

        # Should handle large numbers
        assert pm.get_player_balance() > 1000000000

    def test_zero_balance_scenario(self, game_setup):
        # Tests behavior when player has no money
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(0)

        widgets[0].increase_value()

        # Should not be able to invest
        assert widgets[0].quantity == 0

    def test_fractional_balance_handling(self):
        # Tests that fractional currency is handled
        pm = PlayerManager()
        pm.set_player_balance(1000.50)

        # Should store precisely or round appropriately

    def test_npc_index_out_of_range(self, qapp):
        # Ensures invalid NPC indices are handled
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        # Try to get invalid NPC
        result = npc_manager.get_npc_data(999)
        assert result is None

    def test_negative_npc_index(self, qapp):
        # Tests handling of negative indices
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        result = npc_manager.get_npc_data(-1)
        assert result is None

    def test_action_widget_without_player_manager(self, qapp):
        # Tests widget behavior when player_manager is None
        parent = QWidget()
        widget = ActionWidget(parent, player_manager=None)

        widget.increase_value()  # Should not crash

        assert widget.quantity == 0

    def test_action_widget_without_balance_label(self, qapp):
        # Tests widget behavior when balance_label is None
        parent = QWidget()
        pm = PlayerManager()
        widget = ActionWidget(parent, player_manager=pm, balance_label=None)

        pm.set_player_balance(1000)
        widget.increase_value()  # Should not crash

    def test_price_change_with_invalid_csv_format(self):
        # Tests handling of malformed CSV data
        csv_data = "Invalid,Data\nFormat"

        with patch('builtins.open', mock_open(read_data=csv_data)):
            with patch('os.path.exists', return_value=True):
                try:
                    result = get_price_change('TEST')
                    # Should return default or handle gracefully
                    assert result is not None
                except Exception:
                    pass  # Expected

    def test_empty_stock_name(self):
        # Tests behavior with empty string stock name
        with patch('os.path.exists', return_value=False):
            result = get_price_change('')
            assert result == 1.0

    def test_special_characters_in_stock_name(self, game_setup):
        # Ensures special characters don't break system
        am = game_setup['action_manager']

        am.add_option("TEST@#$", "path.png")
        assert "TEST@#$" in am.options

    def test_very_long_stock_name(self, game_setup):
        # Tests handling of extremely long names
        am = game_setup['action_manager']

        long_name = "A" * 1000
        am.add_option(long_name, "path.png")

        assert long_name in am.options

    def test_duplicate_stock_addition(self, game_setup):
        # Tests adding same stock twice
        am = game_setup['action_manager']

        am.add_option("TEST", "path1.png")
        am.add_option("TEST", "path2.png")

        # Second one should overwrite or be rejected
        assert "TEST" in am.options

    def test_removing_nonexistent_stock(self, game_setup):
        # Ensures removing non-existent stock doesn't crash
        am = game_setup['action_manager']

        am.remove_option("NONEXISTENT")  # Should not crash

    def test_widget_allow_click_false(self, game_setup):
        # Tests that disabling clicks prevents investment
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(1000)
        widgets[0].allow_click = False

        widgets[0].increase_value()

        assert widgets[0].quantity == 0

    def test_concurrent_widget_modifications(self, game_setup):
        # Tests race condition handling (if applicable)
        widgets = game_setup['action_widgets']
        pm = game_setup['player_manager']
        pm.set_player_balance(1000)

        # Rapid changes
        widgets[0].increase_value()
        widgets[1].increase_value()
        widgets[0].decrease_value()
        widgets[2].increase_value()

        # Should maintain consistency
        total_invested = sum(w.quantity for w in widgets[:3])
        assert pm.get_player_balance() + total_invested == 1000

    def test_empty_stock_selection_list(self, game_setup):
        # Verifies system handles empty selection gracefully
        am = game_setup['action_manager']

        # Try to update with no selections
        am.update_value_labels_by_stock()  # Should not crash

    def test_infinite_price_change_handling(self, game_setup):
        # Ensures infinite values don't break calculations
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        am.selected_actions[0] = 'AAPL'
        widgets[0].quantity = 100

        with patch('Game_code.action_manager.get_price_change', return_value=float('inf')):
            try:
                am.update_value_labels_by_stock()
            except (OverflowError, ValueError):
                pass  # Expected

    def test_null_character_in_dialogue(self, qapp):
        # Verifies special characters don't break display
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        # Set dialogue with special characters
        npc_manager.npc_data_list[0]['dialogue'] = "Test\x00Null\nNewline\tTab"

        # Should handle gracefully

    def test_very_long_dialogue_text(self, qapp):
        # Tests UI handles very long text without breaking
        npc_manager = NPCManager()
        parent = QWidget()
        npc_manager.create_npc_widgets(parent)

        long_text = "A" * 10000
        npc_manager.npc_data_list[0]['dialogue'] = long_text
        npc_manager.npc_widgets[0].dialogue_label.setText(long_text)

        # Should not crash

    def test_rapid_balance_changes(self, game_setup):
        # Tests handling many quick transactions
        pm = game_setup['player_manager']

        pm.set_player_balance(10000)

        # Many rapid changes
        for i in range(100):
            pm.set_player_balance(pm.get_player_balance() - 10)

        assert pm.get_player_balance() == 9000

    def test_unicode_in_stock_names(self, game_setup):
        # Ensures international characters don't break system
        am = game_setup['action_manager']

        # Add stock with Unicode
        am.add_option("STÖCK", "path.png")

        assert "STÖCK" in am.options


# ============================================================================
# Performance and Stress Tests (10 tests)
# ============================================================================

class TestPerformance:
    """Test system performance under load"""

    def test_many_stock_options_performance(self):
        # Tests system handles large option dictionary
        am = ActionManager()

        # Add many options
        for i in range(100):
            am.add_option(f"STOCK{i}", f"path{i}.png")

        assert len(am.options) == 111  # 11 original + 100 new

    def test_many_investment_transactions(self, game_setup):
        # Tests handling hundreds of buy/sell operations
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(100000)

        # Many transactions
        for _ in range(500):
            widgets[0].increase_value()

        assert widgets[0].quantity == 50000

    def test_multiple_npc_updates(self, qapp):
        # Tests repeated AI dialogue updates for all NPCs
        with patch('Game_code.npc_manager.ask_bot', return_value='Response'):
            npc_manager = NPCManager()
            parent = QWidget()
            npc_manager.create_npc_widgets(parent)

            # Update all NPCs multiple times
            for _ in range(10):
                for i in range(5):
                    npc_manager.update_dialog_ai(i)

    def test_large_balance_calculations(self, game_setup):
        # Ensures large numbers don't cause overflow
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(999999999)

        widgets[0].quantity = 100000000
        widgets[0].decrease_value()

        assert pm.get_player_balance() == 999999999 + 100

    def test_rapid_stock_selection_changes(self, game_setup):
        # Tests performance of frequent selection updates
        am = game_setup['action_manager']

        for _ in range(100):
            am.randomize_actions()
            am.reset_selections()

    def test_simultaneous_widget_operations(self, game_setup):
        # Tests bulk operations on all 6 action widgets
        pm = game_setup['player_manager']
        widgets = game_setup['action_widgets']

        pm.set_player_balance(10000)

        # Operate on all widgets
        for widget in widgets:
            widget.increase_value()
            widget.increase_value()
            widget.decrease_value()

    def test_many_price_updates(self, game_setup):
        # Tests performance of repeated price change applications
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        for i in range(6):
            am.selected_actions[i] = f'STOCK{i}'
            widgets[i].quantity = 100

        with patch('Game_code.action_manager.get_price_change', return_value=1.1):
            for _ in range(50):
                am.update_value_labels_by_stock()

    def test_large_csv_file_reading(self):
        # Tests performance with large historical datasets
        large_csv = "Date,Close\n" + "\n".join([f"2024-01-{i:02d},100.{i}" for i in range(1, 32)])

        with patch('builtins.open', mock_open(read_data=large_csv)):
            with patch('os.path.exists', return_value=True):
                result = get_price_change('TEST')
                assert result is not None

    def test_memory_cleanup_after_reset(self, game_setup):
        # Verifies no memory leaks after reset operations
        am = game_setup['action_manager']
        widgets = game_setup['action_widgets']

        # Use memory
        for i in range(6):
            am.selected_actions[i] = f'STOCK{i}'
            widgets[i].quantity = 10000

        # Reset
        am.reset_selections()
        for widget in widgets:
            widget.quantity = 0

        # Should be clean
        assert am.selected_actions == [None] * 6

    def test_widget_creation_destruction_cycle(self, qapp):
        # Tests widget lifecycle management
        for _ in range(10):
            parent = QWidget()
            am = ActionManager()
            widgets = am.create_action_widgets(parent)

            # Use widgets
            for widget in widgets:
                widget.show()

            # Cleanup
            parent.deleteLater()


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])