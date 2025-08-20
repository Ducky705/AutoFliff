import os
import sys
import logging
import time
from datetime import datetime
from typing import Optional

from fliff_automator import FliffAutomator
from github_api_manager import GitHubAPIManager
from telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fliff_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FliffBotOrchestrator:
    """Main orchestrator for the Fliff betting bot."""
    
    def __init__(self):
        self.goal_balance = 10.00
        self.min_bet_threshold = 1.80
        self.min_payout_threshold = 50.00
        self.max_payout_threshold = 100.00
        
        # Initialize components
        self.automator = FliffAutomator()
        self.github_manager = GitHubAPIManager()
        self.telegram_notifier = TelegramNotifier()
        
        logger.info("Fliff Bot Orchestrator initialized")
    
    def run(self):
        """Main execution method with comprehensive error handling."""
        screenshot_path = None
        
        try:
            logger.info("Starting Fliff Bot execution")
            
            # Send initial status update
            self.telegram_notifier.send_status_update("Bot started execution")
            
            # Initialize browser and login
            logger.info("Initializing browser and logging in")
            self.automator.login()
            
            # First action: Check if goal is already met
            logger.info("Checking current balance against goal")
            balance = self.automator.get_balance()
            logger.info(f"Current balance: ${balance:,.2f}")
            
            if balance >= self.goal_balance:
                logger.info(f"Goal of ${self.goal_balance:,.2f} already met!")
                self.telegram_notifier.send_success_notification(balance)
                self.github_manager.disable_workflow()
                return
            
            # Check for open wagers that might block collection
            logger.info("Checking for open wagers")
            has_blocking_wagers = self.automator.check_open_wagers()
            
            # Action Phase 1: Resource Collection
            if balance < self.min_bet_threshold and not has_blocking_wagers:
                logger.info("Balance below threshold, attempting to collect rewards")
                self.automator.check_and_claim_rewards()
                
                # Re-check balance after claiming rewards
                balance = self.automator.get_balance()
                logger.info(f"Balance after rewards: ${balance:,.2f}")
                
                if balance < self.min_bet_threshold:
                    logger.info(f"Balance still below minimum bet threshold (${self.min_bet_threshold:,.2f})")
                    self.telegram_notifier.send_status_update(
                        f"Rewards collected but balance still insufficient for betting. "
                        f"Current balance: ${balance:,.2f}"
                    )
                    return
            
            # Action Phase 2: Parlay Construction & Betting
            if balance >= self.min_bet_threshold and not has_blocking_wagers:
                logger.info("Balance sufficient for betting and no blocking wagers, constructing parlay")
                bet_placed = self.automator.execute_betting_strategy(
                    min_payout=self.min_payout_threshold,
                    max_payout=self.max_payout_threshold
                )
                
                if bet_placed:
                    logger.info("Bet placed successfully")
                    # Take screenshot of completed bet slip
                    screenshot_path = self.automator.take_bet_screenshot()
                    
                    # Get final bet details
                    final_balance = self.automator.get_balance()
                    potential_payout = self.automator.get_current_payout()
                    
                    # Send confirmation
                    self.telegram_notifier.send_bet_confirmation(
                        wager_amount=final_balance,
                        potential_potential_payout=potential_payout,
                        screenshot_path=screenshot_path
                    )
                else:
                    logger.info("No suitable parlay could be constructed")
                    self.telegram_notifier.send_status_update(
                        "No suitable parlay could be constructed from available games. "
                        "Will try again on next scheduled run."
                    )
            
            logger.info("Fliff Bot execution completed successfully")
            
        except Exception as e:
            logger.error(f"Critical error in Fliff Bot execution: {e}")
            screenshot_path = self.automator.take_error_screenshot()
            self.telegram_notifier.send_error_notification(str(e), screenshot_path)
            
        finally:
            # Cleanup
            logger.info("Performing cleanup")
            try:
                self.automator.close()
                
                # Clean up screenshot files
                if screenshot_path and os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                    logger.info(f"Cleaned up screenshot: {screenshot_path}")
                    
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

def main():
    """Entry point for the Fliff bot."""
    try:
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Bot execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()