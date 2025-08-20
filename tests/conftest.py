"""
Pytest configuration and shared fixtures for Fliff Bot tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        'FLIFF_USERNAME': 'test_user',
        'FLIFF_PASSWORD': 'test_password',
        'GITHUB_TOKEN': 'test_github_token',
        'GITHUB_REPOSITORY': 'test/test-repo',
        'TELEGRAM_BOT_TOKEN': 'test_telegram_token',
        'TELEGRAM_CHAT_ID': 'test_chat_id',
        'GEOLOCATION_LATITUDE': '40.7128',
        'GEOLOCATION_LONGITUDE': '-74.0060'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for GitHub API calls"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {
            'workflows': [
                {
                    'id': 12345,
                    'path': '.github/workflows/main.yml',
                    'state': 'active'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_requests_put():
    """Mock requests.put for GitHub API calls"""
    with patch('requests.put') as mock_put:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        yield mock_put

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot"""
    with patch('telegram.Bot') as mock_bot_class:
        mock_bot = Mock()
        mock_bot_class.return_value = mock_bot
        yield mock_bot

@pytest.fixture
def mock_playwright():
    """Mock Playwright browser automation"""
    with patch('fliff_automator.sync_playwright') as mock_playwright:
        mock_playwright_instance = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        yield {
            'playwright': mock_playwright_instance,
            'browser': mock_browser,
            'context': mock_context,
            'page': mock_page
        }

@pytest.fixture
def sample_workflows_response():
    """Sample GitHub workflows API response"""
    return {
        'workflows': [
            {
                'id': 12345,
                'path': '.github/workflows/main.yml',
                'state': 'active',
                'updated_at': '2023-01-01T00:00:00Z'
            }
        ]
    }

@pytest.fixture
def sample_balance_data():
    """Sample balance data for testing"""
    return {
        'balance': 5.50,
        'currency': 'USD'
    }

@pytest.fixture
def sample_games_data():
    """Sample games data for testing"""
    return [
        {
            'id': 1,
            'home_team': 'Team A',
            'away_team': 'Team B',
            'proposals': [
                {
                    'team': 'Team A',
                    'odds': '-150',
                    'type': 'moneyline'
                },
                {
                    'team': 'Team B', 
                    'odds': '+130',
                    'type': 'moneyline'
                }
            ]
        }
    ]