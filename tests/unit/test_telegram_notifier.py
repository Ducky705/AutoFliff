"""
Unit tests for TelegramNotifier
"""
import pytest
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
from telegram import Bot, InputFile
from telegram.error import TelegramError
from telegram_notifier import TelegramNotifier


class TestTelegramNotifier:
    """Test cases for TelegramNotifier class"""
    
    def test_init_success(self, mock_env_vars):
        """Test successful initialization with proper environment variables"""
        notifier = TelegramNotifier()
        
        assert notifier.bot_token == 'test_telegram_token'
        assert notifier.chat_id == 'test_chat_id'
        assert isinstance(notifier.bot, Bot)
    
    def test_init_missing_bot_token(self):
        """Test initialization failure when TELEGRAM_BOT_TOKEN is missing"""
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '', 'TELEGRAM_CHAT_ID': 'test_chat_id'}, clear=False):
            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN environment variable is required"):
                TelegramNotifier()
    
    def test_init_missing_chat_id(self, mock_env_vars):
        """Test initialization failure when TELEGRAM_CHAT_ID is missing"""
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': ''}, clear=False):
            with pytest.raises(ValueError, match="TELEGRAM_CHAT_ID environment variable is required"):
                TelegramNotifier()
    
    @patch('telegram_notifier.Bot')
    def test_send_message_success(self, mock_bot_class, mock_env_vars):
        """Test successful message sending"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_message("Test message", parse_mode='HTML')
        
        assert result is True
        
        # Verify bot was called correctly
        mock_bot.send_message.assert_called_once_with(
            chat_id='test_chat_id',
            text='Test message',
            parse_mode='HTML'
        )
    
    @patch('telegram_notifier.Bot')
    def test_send_message_failure(self, mock_bot_class, mock_env_vars):
        """Test message sending failure"""
        # Mock bot instance with error
        mock_bot = Mock()
        mock_bot.send_message.side_effect = TelegramError("Failed to send message")
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_message("Test message")
        
        assert result is False
    
    @patch('telegram_notifier.Bot')
    def test_send_message_unexpected_error(self, mock_bot_class, mock_env_vars):
        """Test message sending with unexpected error"""
        # Mock bot instance with unexpected error
        mock_bot = Mock()
        mock_bot.send_message.side_effect = Exception("Unexpected error")
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_message("Test message")
        
        assert result is False
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_photo_success(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test successful photo sending"""
        # Create a temporary file for testing
        photo_path = tmp_path / "test_photo.jpg"
        photo_path.write_text("fake photo content")
        
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_photo(str(photo_path), "Test caption")
        
        assert result is True
        
        # Verify bot was called correctly
        mock_bot.send_photo.assert_called_once()
        call_args = mock_bot.send_photo.call_args
        assert call_args[1]['chat_id'] == 'test_chat_id'
        assert call_args[1]['caption'] == "Test caption"
        assert isinstance(call_args[1]['photo'], InputFile)
    
    @patch('telegram_notifier.Bot')
    def test_send_photo_file_not_found(self, mock_bot_class, mock_env_vars):
        """Test photo sending when file doesn't exist"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_photo("nonexistent_photo.jpg", "Test caption")
        
        assert result is False
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_photo_failure(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test photo sending failure"""
        # Create a temporary file for testing
        photo_path = tmp_path / "test_photo.jpg"
        photo_path.write_text("fake photo content")
        
        # Mock bot instance with error
        mock_bot = Mock()
        mock_bot.send_photo.side_effect = TelegramError("Failed to send photo")
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_photo(str(photo_path), "Test caption")
        
        assert result is False
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_photo_unexpected_error(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test photo sending with unexpected error"""
        # Create a temporary file for testing
        photo_path = tmp_path / "test_photo.jpg"
        photo_path.write_text("fake photo content")
        
        # Mock bot instance with unexpected error
        mock_bot = Mock()
        mock_bot.send_photo.side_effect = Exception("Unexpected error")
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_photo(str(photo_path), "Test caption")
        
        assert result is False
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_success_notification(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test success notification with screenshot"""
        # Create a temporary file for testing
        screenshot_path = tmp_path / "success_screenshot.jpg"
        screenshot_path.write_text("fake screenshot content")
        
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_success_notification(10.50, str(screenshot_path))
        
        assert result is True
        
        # Verify both message and photo were sent
        assert mock_bot.send_message.call_count == 1
        assert mock_bot.send_photo.call_count == 1
        
        # Check message content
        message_call = mock_bot.send_message.call_args
        assert "SUCCESS" in message_call[1]['text']
        assert "$10.50" in message_call[1]['text']
        assert "Goal: $10.00 ✓" in message_call[1]['text']
    
    @patch('telegram_notifier.Bot')
    def test_send_success_notification_no_screenshot(self, mock_bot_class, mock_env_vars):
        """Test success notification without screenshot"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_success_notification(10.50)
        
        assert result is True
        
        # Verify only message was sent
        mock_bot.send_message.assert_called_once()
        mock_bot.send_photo.assert_not_called()
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_bet_confirmation(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test bet confirmation with screenshot"""
        # Create a temporary file for testing
        screenshot_path = tmp_path / "bet_screenshot.jpg"
        screenshot_path.write_text("fake screenshot content")
        
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_bet_confirmation(5.00, 25.50, str(screenshot_path))
        
        assert result is True
        
        # Verify both message and photo were sent
        assert mock_bot.send_message.call_count == 1
        assert mock_bot.send_photo.call_count == 1
        
        # Check message content
        message_call = mock_bot.send_message.call_args
        assert "BET PLACED SUCCESSFULLY" in message_call[1]['text']
        assert "$5.00" in message_call[1]['text']
        assert "$25.50" in message_call[1]['text']
    
    @patch('telegram_notifier.Bot')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake image data')
    def test_send_error_notification(self, mock_file, mock_bot_class, mock_env_vars, tmp_path):
        """Test error notification with screenshot"""
        # Create a temporary file for testing
        screenshot_path = tmp_path / "error_screenshot.jpg"
        screenshot_path.write_text("fake screenshot content")
        
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_error_notification("Test error message", str(screenshot_path))
        
        assert result is True
        
        # Verify both message and photo were sent
        assert mock_bot.send_message.call_count == 1
        assert mock_bot.send_photo.call_count == 1
        
        # Check message content
        message_call = mock_bot.send_message.call_args
        assert "ERROR" in message_call[1]['text']
        assert "Test error message" in message_call[1]['text']
    
    @patch('telegram_notifier.Bot')
    def test_send_error_notification_no_screenshot(self, mock_bot_class, mock_env_vars):
        """Test error notification without screenshot"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_error_notification("Test error message")
        
        assert result is True
        
        # Verify only message was sent
        mock_bot.send_message.assert_called_once()
        mock_bot.send_photo.assert_not_called()
    
    @patch('telegram_notifier.Bot')
    def test_send_status_update(self, mock_bot_class, mock_env_vars):
        """Test status update"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        
        notifier = TelegramNotifier()
        result = notifier.send_status_update("Test status message")
        
        assert result is True
        
        # Verify message was sent with timestamp
        mock_bot.send_message.assert_called_once()
        message_call = mock_bot.send_message.call_args
        assert "STATUS UPDATE" in message_call[1]['text']
        assert "Test status message" in message_call[1]['text']
    
    @patch('telegram_notifier.Bot')
    def test_send_message_without_parse_mode(self, mock_bot_class, mock_env_vars):
        """Test message sending without parse mode"""
        # Mock bot instance
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot

        notifier = TelegramNotifier()
        result = notifier.send_message("Test message")

        assert result is True

        # Verify bot was called with parse_mode=None when not specified
        mock_bot.send_message.assert_called_once_with(
            chat_id='test_chat_id',
            text='Test message',
            parse_mode=None
        )
    
    def test_bot_token_property(self, mock_env_vars):
        """Test bot_token property"""
        notifier = TelegramNotifier()
        assert notifier.bot_token == 'test_telegram_token'
    
    def test_chat_id_property(self, mock_env_vars):
        """Test chat_id property"""
        notifier = TelegramNotifier()
        assert notifier.chat_id == 'test_chat_id'
    
    def test_bot_property(self, mock_env_vars):
        """Test bot property"""
        notifier = TelegramNotifier()
        assert isinstance(notifier.bot, Bot)