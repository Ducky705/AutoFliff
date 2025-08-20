import os
import logging
import time
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, ElementHandle

logger = logging.getLogger(__name__)

class FliffAutomator:
    """Core browser automation for Fliff interactions."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Configuration
        self.base_url = "https://fliff.com"
        self.latitude = float(os.getenv('GEOLOCATION_LATITUDE', '40.7128'))
        self.longitude = float(os.getenv('GEOLOCATION_LONGITUDE', '-74.0060'))
        
        # Verified UI selectors
        self.selectors = {
            'login_button': ".ticket-submit-button__label:has-text('LOGIN')",
            'location_continue': ".button__label:has-text('Continue')",
            'balance_container': "div.balances__item img[alt*='cash icon'] + span.balances__balance",
            'bet_slip_container': ".mobile-ticket-container",
            'shop_claim_button': ".free-coins-plaque__claim-button",
            'rewards_claim_buttons': ".claim-button",
            'submit_bet_button': ".ticket-submit-button__label:has-text('SUBMIT')",
            'bet_success_confirmation': ".ticket-submit-button__bonus-text:has-text('Claim')"
        }
        
        logger.info("FliffAutomator initialized")
    
    def _setup_browser(self):
        """Initialize browser with mobile emulation."""
        try:
            self.browser = sync_playwright().start().chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-notifications'
                ]
            )
            
            # Mobile emulation context
            self.context = self.browser.new_context(
                viewport={'width': 375, 'height': 812},  # iPhone 13 dimensions
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
                geolocation={'latitude': self.latitude, 'longitude': self.longitude},
                permissions=['geolocation']
            )
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(30000)  # 30 second timeout
            
            logger.info("Browser setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            raise
    
    def _retry_operation(self, operation, max_retries=3, delay=2, operation_name="operation"):
        """Retry an operation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = delay * (2 ** attempt)
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
    
    def login(self):
        """Login to Fliff with retry mechanism."""
        def _login():
            if not self.page:
                self._setup_browser()
            
            logger.info("Navigating to Fliff login page")
            self.page.goto(f"{self.base_url}/login")
            
            # Wait for login button to be visible
            login_button = self.page.wait_for_selector(self.selectors['login_button'])
            if not login_button:
                raise Exception("Login button not found")
            
            logger.info("Entering credentials")
            self.page.fill('input[type="text"]', os.getenv('FLIFF_USERNAME'))
            self.page.fill('input[type="password"]', os.getenv('FLIFF_PASSWORD'))
            
            # Click login button
            login_button.click()
            
            # Handle location prompt
            try:
                location_continue = self.page.wait_for_selector(self.selectors['location_continue'], timeout=5000)
                if location_continue:
                    location_continue.click()
                    logger.info("Location prompt handled")
            except:
                logger.info("No location prompt found")
            
            # Wait for navigation to complete
            self.page.wait_for_load_state('networkidle')
            logger.info("Login completed successfully")
        
        self._retry_operation(_login, operation_name="login")
    
    def get_balance(self) -> float:
        """Get current Fliff Cash balance."""
        def _get_balance():
            logger.info("Fetching current balance")
            
            # Navigate to account page
            self.page.click('div.nav-account')
            self.page.wait_for_load_state('networkidle')
            
            # Parse balance using verified selector
            balance_element = self.page.wait_for_selector(self.selectors['balance_container'])
            if not balance_element:
                raise Exception("Balance element not found")
            
            balance_text = balance_element.text_content().strip()
            # Remove commas and convert to float
            balance_clean = re.sub(r'[,$]', '', balance_text)
            balance = float(balance_clean)
            
            logger.info(f"Current balance: ${balance:,.2f}")
            return balance
        
        return self._retry_operation(_get_balance, operation_name="get_balance")
    
    def check_open_wagers(self) -> bool:
        """Check if there are open wagers that might block collection."""
        def _check_wagers():
            logger.info("Checking for open wagers")
            
            # Navigate to activity page
            self.page.click('a[href="/activity"]')
            self.page.wait_for_load_state('networkidle')
            
            # Look for bet slips
            bet_slips = self.page.query_selector_all('.bet-slip')
            if not bet_slips:
                logger.info("No open wagers found")
                return False
            
            # Check if any bet has payout > $1.80
            for slip in bet_slips:
                payout_text = slip.text_content()
                if 'payout' in payout_text.lower():
                    # Extract numeric value
                    payout_match = re.search(r'[\d,]+', payout_text)
                    if payout_match:
                        payout = float(payout_match.group().replace(',', ''))
                        if payout > 1.80:
                            logger.info(f"Found blocking wager with payout: ${payout:,.2f}")
                            return True
            
            logger.info("No blocking wagers found")
            return False
        
        return self._retry_operation(_check_wagers, operation_name="check_open_wagers")
    
    def check_and_claim_rewards(self):
        """Claim available daily and bi-hourly rewards."""
        def _claim_rewards():
            logger.info("Checking and claiming rewards")
            
            # Navigate to shop
            self.page.click('a[href="/shop"]')
            self.page.wait_for_load_state('networkidle')
            
            # Claim shop rewards
            shop_claim = self.page.query_selector(self.selectors['shop_claim_button'])
            if shop_claim:
                shop_claim.click()
                logger.info("Shop rewards claimed")
                time.sleep(2)  # Wait for animation
            
            # Navigate to rewards
            self.page.click('a[href="/rewards"]')
            self.page.wait_for_load_state('networkidle')
            
            # Claim other rewards
            reward_buttons = self.page.query_selector_all(self.selectors['rewards_claim_buttons'])
            claimed_count = 0
            for button in reward_buttons:
                if 'claim' in button.text_content().lower():
                    button.click()
                    claimed_count += 1
                    time.sleep(1)  # Wait between claims
            
            logger.info(f"Claimed {claimed_count} additional rewards")
        
        self._retry_operation(_claim_rewards, operation_name="claim_rewards")
    
    def execute_betting_strategy(self, min_payout: float, max_payout: float) -> bool:
        """Execute parlay construction strategy."""
        def _execute_strategy():
            logger.info(f"Executing betting strategy (target payout: ${min_payout:,.2f}-${max_payout:,.2f})")
            
            # Navigate to sports page
            self.page.click('a[href="/sports"]')
            self.page.wait_for_load_state('networkidle')
            
            # Get available games
            games = self.page.query_selector_all('div.card-shared-container')
            if not games:
                logger.warning("No games found")
                return False
            
            # Filter for safe odds (-250 to +200)
            safe_games = []
            for game in games:
                try:
                    proposals = game.query_selector_all('div.card-home-proposal:not(:has(img[alt="lock"]))')
                    for proposal in proposals:
                        odds_text = proposal.query_selector('.card-cell-label').text_content().strip()
                        odds_decimal = self._convert_odds_to_decimal(odds_text)
                        
                        if -250 <= odds_decimal <= 200:
                            safe_games.append({
                                'element': proposal,
                                'odds': odds_decimal,
                                'game': game
                            })
                except Exception as e:
                    logger.warning(f"Error processing game: {e}")
                    continue
            
            if not safe_games:
                logger.warning("No games with safe odds found")
                return False
            
            # Build parlay
            current_payout = 1.0
            parlay_selections = []
            
            for game_data in safe_games:
                if current_payout >= max_payout:
                    break
                
                # Add selection to parlay
                game_data['element'].click()
                time.sleep(1)  # Wait for bet slip update
                
                # Get updated payout
                current_payout = self._get_current_payout()
                parlay_selections.append(game_data)
                
                logger.info(f"Added selection, current payout: ${current_payout:,.2f}")
                
                if min_payout <= current_payout <= max_payout:
                    logger.info(f"Target payout reached: ${current_payout:,.2f}")
                    return True
            
            logger.info(f"Parlay construction completed with ${current_payout:,.2f} payout")
            return current_payout >= min_payout
        
        return self._retry_operation(_execute_strategy, operation_name="betting_strategy")
    
    def _convert_odds_to_decimal(self, odds_text: str) -> float:
        """Convert American odds to decimal multiplier."""
        odds_text = odds_text.strip()
        
        if odds_text.startswith('+'):
            return (float(odds_text[1:]) + 100) / 100
        elif odds_text.startswith('-'):
            return (100 + float(odds_text[1:])) / float(odds_text[1:])
        else:
            return float(odds_text)
    
    def _get_current_payout(self) -> float:
        """Get current parlay payout from bet slip."""
        bet_slip = self.page.wait_for_selector(self.selectors['bet_slip_container'])
        if not bet_slip:
            return 0.0
        
        # Look for payout amount
        payout_text = bet_slip.text_content()
        # Match numbers with commas and decimals
        payout_match = re.search(r'[\d,]+\.?\d*', payout_text)
        
        if payout_match:
            # Remove commas and convert to float
            payout_str = payout_match.group().replace(',', '')
            return float(payout_str)
        
        return 0.0
    
    def place_bet(self, wager_amount: float) -> bool:
        """Place the bet with specified amount."""
        def _place_bet():
            logger.info(f"Placing bet with amount: ${wager_amount:,.2f}")
            
            # Take screenshot before bet
            screenshot_path = self.take_bet_screenshot()
            
            # Enter wager amount
            wager_input = self.page.wait_for_selector('.risk-amount-input__amount')
            wager_input.click()
            wager_input.fill(str(int(wager_amount)))
            
            # Submit bet
            submit_button = self.page.wait_for_selector(self.selectors['submit_bet_button'])
            submit_button.click()
            
            # Wait for confirmation
            self.page.wait_for_selector(self.selectors['bet_success_confirmation'])
            
            logger.info("Bet placed successfully")
            return True
        
        return self._retry_operation(_place_bet, operation_name="place_bet")
    
    def take_bet_screenshot(self) -> str:
        """Take screenshot of bet slip before submission."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"screenshots/bet_slip_{timestamp}.png"
        
        try:
            bet_slip = self.page.wait_for_selector(self.selectors['bet_slip_container'])
            bet_slip.screenshot(path=screenshot_path)
            logger.info(f"Bet slip screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take bet slip screenshot: {e}")
            return ""
    
    def take_error_screenshot(self) -> str:
        """Take full-page error screenshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"screenshots/error_{timestamp}.png"
        
        try:
            self.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Error screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take error screenshot: {e}")
            return ""
    
    def close(self):
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            logger.error(f"Error during context cleanup: {e}")
        
        try:
            if self.browser:
                self.browser.close()
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
        
        logger.info("Browser resources cleaned up")