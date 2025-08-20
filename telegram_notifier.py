import os
import logging
from datetime import datetime
from typing import Optional
from telegram import Bot, InputFile
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Handles all Telegram messaging for the Fliff bot."""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable is required")
        
        self.bot = Bot(token=self.bot_token)
    
    def send_message(self, message: str, parse_mode: Optional[str] = None) -> bool:
        """
        Send a text message to Telegram.
        
        Args:
            message: The message text to send
            parse_mode: Optional HTML or Markdown parse mode
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("Message sent successfully to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def send_photo(self, photo_path: str, caption: Optional[str] = None) -> bool:
        """
        Send a photo to Telegram with optional caption.
        
        Args:
            photo_path: Path to the photo file
            caption: Optional caption for the photo
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(photo_path):
                logger.error(f"Photo file not found: {photo_path}")
                return False
            
            with open(photo_path, 'rb') as photo_file:
                self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=InputFile(photo_file),
                    caption=caption
                )
            
            logger.info(f"Photo sent successfully to Telegram: {photo_path}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram photo: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram photo: {e}")
            return False
    
    def send_success_notification(self, balance: float, screenshot_path: Optional[str] = None) -> bool:
        """
        Send success notification when $10.00 goal is reached.
        
        Args:
            balance: Current account balance
            screenshot_path: Optional screenshot path
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"🎉 SUCCESS: Fliff Bot Goal Achieved! 🎉\n\n"
        message += f"Current Balance: ${balance:,.2f}\n"
        message += f"Goal: $10.00 ✓\n\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "The bot has been successfully terminated and will not run again until manually re-enabled."
        
        success = self.send_message(message, parse_mode='HTML')
        
        if screenshot_path and success:
            success = self.send_photo(screenshot_path, "Final balance screenshot")
        
        return success
    
    def send_bet_confirmation(self, wager_amount: float, potential_payout: float, screenshot_path: str) -> bool:
        """
        Send bet confirmation with screenshot.
        
        Args:
            wager_amount: Amount wagered
            potential_payout: Potential payout amount
            screenshot_path: Path to bet slip screenshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"🎯 BET PLACED SUCCESSFULLY! 🎯\n\n"
        message += f"Wager Amount: ${wager_amount:,.2f}\n"
        message += f"Potential Payout: ${potential_payout:,.2f}\n\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "Bet slip screenshot attached below:"
        
        success = self.send_message(message, parse_mode='HTML')
        
        if success:
            success = self.send_photo(screenshot_path, "Bet slip confirmation")
        
        return success
    
    def send_error_notification(self, error_message: str, screenshot_path: Optional[str] = None) -> bool:
        """
        Send error notification with optional screenshot.
        
        Args:
            error_message: Error message to send
            screenshot_path: Optional error screenshot path
            
        Returns:
            bool: True if successful, False otherwise
        """
        message = f"❌ ERROR: Fliff Bot Encountered an Issue ❌\n\n"
        message += f"Error: {error_message}\n\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "Please check the logs and screenshot for debugging information."
        
        success = self.send_message(message, parse_mode='HTML')
        
        if screenshot_path and success:
            success = self.send_photo(screenshot_path, "Error screenshot")
        
        return success
    
    def send_status_update(self, message: str) -> bool:
        """
        Send general status update.
        
        Args:
            message: Status message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"📊 STATUS UPDATE: {timestamp}\n\n{message}"
        
        return self.send_message(full_message, parse_mode='HTML')