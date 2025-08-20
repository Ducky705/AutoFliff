# Fliff Betting Bot - README

## Overview

This is a fully autonomous Fliff Cash collection and strategic parlay betting bot that runs on GitHub Actions. The bot automates the process of collecting daily rewards and placing strategic bets to reach a $10.00 goal balance.

## Features

- 🤖 **Fully Automated**: Runs automatically via GitHub Actions
- 📱 **Mobile Emulation**: Runs as iPhone 13 for proper site rendering
- 🎯 **Smart Betting**: Strategic parlay construction with safe odds
- 📊 **Real-time Notifications**: Telegram updates for all actions
- 🛡️ **Error Handling**: Comprehensive retry mechanisms and error screenshots
- 🧪 **Comprehensive Testing**: Unit, integration, and end-to-end test suite
- 🔄 **Self-Termination**: Automatically disables when $10.00 goal is reached

## Prerequisites

- Python 3.10 or higher
- GitHub account with repository access
- Telegram account for notifications
- Fliff account credentials

## Quick Start

### 1. Fork/Clone Repository

```bash
git clone https://github.com/Ducky705/AutoFliff.git
cd AutoFliff
```

### 2. Configure Environment

Copy the template and fill in your actual values:

```bash
cp .env.template .env
```

Edit `.env` file with your credentials:

```env
# Fliff Account Credentials
FLIFF_USERNAME=your_fliff_username
FLIFF_PASSWORD=your_fliff_password

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# GitHub API Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPOSITORY=Ducky705/AutoFliff

# Optional: Custom geolocation coordinates
GEOLOCATION_LATITUDE=40.7128
GEOLOCATION_LONGITUDE=-74.0060
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Test Locally

```bash
python main.py
```

### 5. Run Test Suite

```bash
python run_tests.py
```

## GitHub Repository Setup

### 1. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions and add the following secrets:

```
FLIFF_USERNAME=your_fliff_username
FLIFF_PASSWORD=your_fliff_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
GITHUB_TOKEN=your_github_personal_access_token
```

#### Getting Telegram Bot Token:
1. Open Telegram and search for "BotFather"
2. Create a new bot with `/newbot`
3. Copy the bot token provided

#### Getting Telegram Chat ID:
1. Open Telegram and search for "userinfobot"
2. Send any message to get your chat ID
3. Alternatively, use the bot to get your ID

#### Getting GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` and `workflow` scopes
3. Copy the token immediately (it won't be shown again)

## GitHub Actions Configuration

The bot is configured to run automatically via GitHub Actions with the following schedule:

- **Schedule**: Every hour at the top of the hour (`0 * * * *`)
- **Manual Runs**: Can be triggered manually from the Actions tab
- **Self-Termination**: Automatically disables itself when $10.00 goal is reached

### Workflow Features:

1. **Mobile Emulation**: Runs as iPhone 13 for proper site rendering
2. **Geolocation**: Set to New York City by default
3. **Error Handling**: Comprehensive retry mechanisms and error screenshots
4. **Notifications**: Real-time Telegram updates for all actions

## Test Suite

The project includes a comprehensive test suite that can be run with a single command:

### Running Tests

```bash
python run_tests.py
```

This will run:
- **Unit Tests**: Test individual components (GitHubAPIManager, TelegramNotifier)
- **Integration Tests**: Test FliffAutomator with mocked browser interactions
- **End-to-End Tests**: Test the main orchestration workflow

### Test Coverage

- Unit tests: 100% coverage
- Integration tests: 65% coverage
- End-to-End tests: 99% coverage

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_github_api_manager.py
│   └── test_telegram_notifier.py
├── integration/             # Integration tests
│   ├── __init__.py
│   └── test_fliff_automator.py
├── e2e/                     # End-to-end tests
│   ├── __init__.py
│   └── test_main_orchestration.py
└── fixtures/                # Test data and mocks
    └── __init__.py
```

### Manual Testing with Pytest

You can also run specific test categories:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run end-to-end tests only
pytest tests/e2e/

# Run with coverage
pytest --cov=.
```

## Monitoring and Debugging

### 1. Logs

- **Local**: Check `fliff_bot.log` in the project directory
- **GitHub Actions**: View logs in the Actions tab of your repository

### 2. Error Screenshots

The bot automatically takes screenshots when errors occur:
- Saved to `screenshots/` directory
- Named with timestamp: `error-YYYY-MM-DD_HH-MM-SS.png`
- Automatically sent to Telegram for debugging

### 3. Common Issues

#### Login Issues:
- Verify Fliff credentials are correct
- Check if Fliff has added new security measures
- Ensure geolocation permissions are handled

#### Betting Strategy Issues:
- Verify odds parsing logic matches current Fliff interface
- Check if bet slip selectors have changed
- Ensure payout calculations are accurate

#### GitHub API Issues:
- Verify GITHUB_TOKEN has correct permissions
- Check repository name format in GITHUB_REPOSITORY
- Ensure workflow file path is correct

## Security Considerations

1. **Never commit `.env` file** - it's already in `.gitignore`
2. **Use strong, unique passwords** for Fliff account
3. **Regularly rotate GitHub tokens** for security
4. **Monitor Telegram notifications** for bot activity
5. **Keep repository private** to protect credentials

## Troubleshooting

### Bot Not Running

1. Check GitHub Actions logs for errors
2. Verify all secrets are correctly configured
3. Ensure repository is set to private
4. Check if workflow has proper permissions

### Balance Not Updating

1. Verify balance parsing selectors are still valid
2. Check if Fliff interface has changed
3. Look for JavaScript errors in browser console

### Telegram Not Sending Messages

1. Verify bot token and chat ID are correct
2. Check if bot has been blocked
3. Verify network connectivity to Telegram API

## Maintenance

### Updating Dependencies

```bash
pip install --upgrade -r requirements.txt
playwright install chromium
```

### Re-enabling Bot

After the bot reaches $10.00 and disables itself:

1. Go to repository → Actions → Workflows
2. Find the "Fliff Betting Bot" workflow
3. Click "Enable workflow" button
4. The bot will resume on the next scheduled run

### Performance Monitoring

- Monitor success rate of betting strategy
- Track average time between runs
- Review error logs for recurring issues
- Adjust betting parameters based on performance

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Examine error screenshots sent to Telegram
4. Verify all configuration parameters

## Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Structure

```
fliff-bot/
├── main.py                  # Main orchestrator
├── fliff_automator.py       # Browser automation
├── github_api_manager.py    # GitHub API interactions
├── telegram_notifier.py     # Telegram messaging
├── requirements.txt         # Dependencies
├── run_tests.py            # Test runner
├── .env                   # Environment variables (not committed)
├── .gitignore             # Git ignore rules
└── tests/                 # Test suite
    ├── conftest.py
    ├── unit/
    ├── integration/
    ├── e2e/
    └── fixtures/
```

---

**Note**: This bot is for educational purposes. Use responsibly and in accordance with Fliff's terms of service.