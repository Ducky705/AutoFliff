"""
Integration tests for FliffAutomator
"""
import pytest
import os
import re
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fliff_automator import FliffAutomator


class TestFliffAutomator:
    """Test cases for FliffAutomator class"""
    
    def test_init_success(self, mock_env_vars):
        """Test successful initialization"""
        automator = FliffAutomator()
        
        assert automator.base_url == "https://fliff.com"
        assert automator.latitude == 40.7128
        assert automator.longitude == -74.0060
        assert automator.browser is None
        assert automator.context is None
        assert automator.page is None
        
        # Verify selectors are properly initialized
        assert 'login_button' in automator.selectors
        assert 'balance_container' in automator.selectors
        assert 'bet_slip_container' in automator.selectors
        assert 'submit_bet_button' in automator.selectors
    
    def test_init_with_custom_geolocation(self):
        """Test initialization with custom geolocation"""
        with patch.dict(os.environ, {
            'GEOLOCATION_LATITUDE': '34.0522',
            'GEOLOCATION_LONGITUDE': '-118.2437'
        }):
            automator = FliffAutomator()
            assert automator.latitude == 34.0522
            assert automator.longitude == -118.2437
    
    @patch('fliff_automator.sync_playwright')
    def test_setup_browser_success(self, mock_sync_playwright, mock_env_vars):
        """Test successful browser setup"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        automator = FliffAutomator()
        automator._setup_browser()
        
        # Verify browser components were set up
        assert automator.browser == mock_browser
        assert automator.context == mock_context
        assert automator.page == mock_page
        
        # Verify browser launch arguments
        mock_playwright_instance.chromium.launch.assert_called_once_with(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-notifications'
            ]
        )
        
        # Verify context creation
        mock_browser.new_context.assert_called_once_with(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation']
        )
        
        # Verify page creation and timeout setting
        mock_context.new_page.assert_called_once()
        mock_page.set_default_timeout.assert_called_once_with(30000)
    
    @patch('fliff_automator.sync_playwright')
    def test_setup_browser_failure(self, mock_sync_playwright, mock_env_vars):
        """Test browser setup failure"""
        # Mock Playwright failure
        mock_sync_playwright.return_value.start.side_effect = Exception("Browser launch failed")
        
        automator = FliffAutomator()
        
        with pytest.raises(Exception, match="Browser launch failed"):
            automator._setup_browser()
    
    @patch('fliff_automator.sync_playwright')
    def test_login_success(self, mock_sync_playwright, mock_env_vars):
        """Test successful login"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock page elements and interactions
        mock_login_button = Mock()
        mock_page.wait_for_selector.return_value = mock_login_button
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        # Inject mock page
        automator.page = mock_page
        automator.login()
        
        # Verify login sequence - allow 1 or 2 clicks (login + optional location prompt)
        mock_page.goto.assert_called_once_with("https://fliff.com/login")
        mock_page.fill.assert_any_call('input[type="text"]', 'test_user')
        mock_page.fill.assert_any_call('input[type="password"]', 'test_password')
        assert mock_login_button.click.call_count >= 1
        
        # Since we're injecting a mock page, Playwright setup shouldn't be called
        mock_sync_playwright.return_value.start.assert_not_called()
    
    @patch('fliff_automator.sync_playwright')
    def test_login_with_location_prompt(self, mock_sync_playwright, mock_env_vars):
        """Test login with location prompt handling"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock page elements and interactions
        mock_login_button = Mock()
        mock_location_continue = Mock()
        mock_page.wait_for_selector.side_effect = [mock_login_button, mock_location_continue]
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        automator.login()
        
        # Verify location prompt was handled
        mock_location_continue.click.assert_called_once()
    
    @patch('fliff_automator.sync_playwright')
    def test_get_balance_success(self, mock_sync_playwright, mock_env_vars):
        """Test successful balance retrieval"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock balance element
        mock_balance_element = Mock()
        mock_balance_element.text_content.return_value = "$5.50"
        mock_page.wait_for_selector.return_value = mock_balance_element
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        # Inject mock page
        automator.page = mock_page
        balance = automator.get_balance()
        
        assert balance == 5.50
        mock_page.click.assert_called_with('div.nav-account')
        mock_balance_element.text_content.assert_called_once()
    
    @patch('fliff_automator.sync_playwright')
    def test_get_balance_with_commas(self, mock_sync_playwright, mock_env_vars):
        """Test balance retrieval with comma formatting"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock balance element with comma
        mock_balance_element = Mock()
        mock_balance_element.text_content.return_value = "$1,000.50"
        mock_page.wait_for_selector.return_value = mock_balance_element
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        automator.page = mock_page
        balance = automator.get_balance()
        
        assert balance == 1000.50
    
    @patch('fliff_automator.sync_playwright')
    def test_check_open_wagers_no_wagers(self, mock_sync_playwright, mock_env_vars):
        """Test checking open wagers when none exist"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock no bet slips found
        mock_page.query_selector_all.return_value = []
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        automator.page = mock_page
        has_wagers = automator.check_open_wagers()
        
        assert has_wagers is False
        mock_page.click.assert_called_with('a[href="/activity"]')
    
    @patch('fliff_automator.sync_playwright')
    def test_check_open_wagers_with_blocking_wager(self, mock_sync_playwright, mock_env_vars):
        """Test checking open wagers with blocking wager"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock bet slip with high payout
        mock_bet_slip = Mock()
        mock_bet_slip.text_content.return_value = "Potential payout: $50.00"
        mock_page.query_selector_all.return_value = [mock_bet_slip]
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        automator.page = mock_page
        has_wagers = automator.check_open_wagers()
        
        assert has_wagers is True
    
    @patch('fliff_automator.sync_playwright')
    def test_check_open_wagers_no_blocking_wager(self, mock_sync_playwright, mock_env_vars):
        """Test checking open wagers with no blocking wager"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock bet slip with low payout
        mock_bet_slip = Mock()
        mock_bet_slip.text_content.return_value = "Potential payout: $1.50"
        mock_page.query_selector_all.return_value = [mock_bet_slip]
        mock_page.wait_for_load_state.return_value = None
        
        automator = FliffAutomator()
        automator.page = mock_page
        has_wagers = automator.check_open_wagers()
        
        assert has_wagers is False
    
    def test_convert_odds_to_decimal_positive(self):
        """Test conversion of positive odds to decimal"""
        automator = FliffAutomator()
        
        # Test positive odds
        decimal_odds = automator._convert_odds_to_decimal("+150")
        assert decimal_odds == 2.5
        
        decimal_odds = automator._convert_odds_to_decimal("+100")
        assert decimal_odds == 2.0
        
        decimal_odds = automator._convert_odds_to_decimal("+200")
        assert decimal_odds == 3.0
    
    def test_convert_odds_to_decimal_negative(self):
        """Test conversion of negative odds to decimal"""
        automator = FliffAutomator()
        # Test negative odds
        decimal_odds = automator._convert_odds_to_decimal("-150")
        assert decimal_odds == pytest.approx(1.6667, abs=0.0001)
        
        decimal_odds = automator._convert_odds_to_decimal("-200")
        assert decimal_odds == 1.5
        
        decimal_odds = automator._convert_odds_to_decimal("-250")
        assert decimal_odds == 1.4
    
    def test_convert_odds_to_decimal_decimal(self):
        """Test conversion of decimal odds"""
        automator = FliffAutomator()
        
        # Test decimal odds
        decimal_odds = automator._convert_odds_to_decimal("2.5")
        assert decimal_odds == 2.5
        
        decimal_odds = automator._convert_odds_to_decimal("1.5")
        assert decimal_odds == 1.5
    
    @patch('fliff_automator.sync_playwright')
    def test_get_current_payout_success(self, mock_sync_playwright, mock_env_vars):
        """Test successful current payout retrieval"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Create automator and inject mock page
        automator = FliffAutomator()
        automator.page = mock_page
        
        # Mock bet slip with payout
        mock_bet_slip = Mock()
        mock_bet_slip.text_content.return_value = "Potential payout: $25.50"
        mock_page.wait_for_selector.return_value = mock_bet_slip

        payout = automator._get_current_payout()
        
        assert payout == pytest.approx(25.50, abs=0.01)
    
    @patch('fliff_automator.sync_playwright')
    def test_get_current_payout_no_payout(self, mock_sync_playwright, mock_env_vars):
        """Test current payout retrieval when no payout found"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Create automator and inject mock page
        automator = FliffAutomator()
        automator.page = mock_page
        
        # Mock bet slip without payout
        mock_bet_slip = Mock()
        mock_bet_slip.text_content.return_value = "No payout information"
        mock_page.wait_for_selector.return_value = mock_bet_slip
        
        payout = automator._get_current_payout()
        
        assert payout == 0.0
    
    @patch('fliff_automator.sync_playwright')
    def test_take_bet_screenshot_success(self, mock_sync_playwright, mock_env_vars, tmp_path):
        """Test successful bet screenshot"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock bet slip
        mock_bet_slip = Mock()
        mock_bet_slip.screenshot.return_value = None
        mock_page.wait_for_selector.return_value = mock_bet_slip
        
        automator = FliffAutomator()
        automator.page = mock_page
        
        # Mock datetime to return predictable timestamp
        with patch('fliff_automator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20231201_120000"
            
            screenshot_path = automator.take_bet_screenshot()
            
            assert screenshot_path == "screenshots/bet_slip_20231201_120000.png"
            mock_bet_slip.screenshot.assert_called_once_with(path=screenshot_path)
    
    @patch('fliff_automator.sync_playwright')
    def test_take_bet_screenshot_failure(self, mock_sync_playwright, mock_env_vars):
        """Test bet screenshot failure"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock bet slip with screenshot failure
        mock_bet_slip = Mock()
        mock_bet_slip.screenshot.side_effect = Exception("Screenshot failed")
        mock_page.wait_for_selector.return_value = mock_bet_slip
        
        automator = FliffAutomator()
        screenshot_path = automator.take_bet_screenshot()
        
        assert screenshot_path == ""
    
    @patch('fliff_automator.sync_playwright')
    def test_take_error_screenshot_success(self, mock_sync_playwright, mock_env_vars, tmp_path):
        """Test successful error screenshot"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        automator = FliffAutomator()
        automator.page = mock_page
        
        # Mock datetime to return predictable timestamp
        with patch('fliff_automator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20231201_120000"
            
            screenshot_path = automator.take_error_screenshot()
            
            assert screenshot_path == "screenshots/error_20231201_120000.png"
            mock_page.screenshot.assert_called_once_with(path=screenshot_path, full_page=True)
    
    @patch('fliff_automator.sync_playwright')
    def test_take_error_screenshot_failure(self, mock_sync_playwright, mock_env_vars):
        """Test error screenshot failure"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock page with screenshot failure
        mock_page.screenshot.side_effect = Exception("Screenshot failed")
        
        automator = FliffAutomator()
        screenshot_path = automator.take_error_screenshot()
        
        assert screenshot_path == ""
    
    @patch('fliff_automator.sync_playwright')
    def test_close_success(self, mock_sync_playwright, mock_env_vars):
        """Test successful cleanup"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        automator = FliffAutomator()
        automator.browser = mock_browser
        automator.context = mock_context
        automator.close()

        # Verify cleanup sequence
        mock_context.close.assert_called()
        mock_browser.close.assert_called_once()
    
    @patch('fliff_automator.sync_playwright')
    def test_close_with_error(self, mock_sync_playwright, mock_env_vars):
        """Test cleanup with error"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()

        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Mock cleanup failure
        mock_context.close.side_effect = Exception("Cleanup failed")

        automator = FliffAutomator()
        automator.browser = mock_browser
        automator.context = mock_context
        # Should not raise exception
        automator.close()

        # Verify cleanup was attempted
        mock_context.close.assert_called()
        mock_browser.close.assert_called()
    
    @patch('fliff_automator.sync_playwright')
    def test_retry_operation_success(self, mock_sync_playwright, mock_env_vars):
        """Test retry operation with success on first attempt"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        automator = FliffAutomator()
        
        # Mock successful operation
        def successful_operation():
            return "success"
        
        result = automator._retry_operation(successful_operation, operation_name="test")
        
        assert result == "success"
    
    @patch('fliff_automator.sync_playwright')
    def test_retry_operation_failure_then_success(self, mock_sync_playwright, mock_env_vars):
        """Test retry operation with success after failure"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        automator = FliffAutomator()
        
        # Mock operation that fails then succeeds
        call_count = 0
        
        def sometimes_failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt failed")
            return "success"
        
        result = automator._retry_operation(sometimes_failing_operation, operation_name="test")
        
        assert result == "success"
    
    @patch('fliff_automator.sync_playwright')
    def test_retry_operation_max_retries_exceeded(self, mock_sync_playwright, mock_env_vars):
        """Test retry operation when max retries exceeded"""
        # Mock Playwright components
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        automator = FliffAutomator()
        
        # Mock always failing operation
        def failing_operation():
            raise Exception("Operation failed")
        
        with pytest.raises(Exception, match="Operation failed"):
            automator._retry_operation(failing_operation, operation_name="test")