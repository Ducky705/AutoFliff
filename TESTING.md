# Fliff Bot Test Suite

This document provides comprehensive information about the test suite for the Fliff Bot application.

## Overview

The test suite is designed to ensure the reliability and correctness of the Fliff Bot through comprehensive testing at multiple levels:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **End-to-End Tests**: Test complete application workflows

## Quick Start

### Prerequisites

Ensure you have Python 3.7+ installed and the project dependencies installed:

```bash
pip install -r requirements.txt
```

### Running Tests

#### Run All Tests (Recommended)

```bash
python run_tests.py
```

This command runs the complete test suite with coverage reporting.

#### Run Specific Test Categories

```bash
# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run only end-to-end tests
python run_tests.py e2e
```

#### Using Pytest Directly

You can also run tests directly using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_github_api_manager.py

# Run specific test
pytest tests/unit/test_github_api_manager.py::TestGitHubAPIManager::test_init_success
```

### Help

```bash
python run_tests.py --help
```

## Test Structure

```
fliff-bot/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures and configuration
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_github_api_manager.py
│   │   └── test_telegram_notifier.py
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   └── test_fliff_automator.py
│   ├── e2e/                        # End-to-end tests
│   │   ├── __init__.py
│   │   └── test_main_orchestration.py
│   └── fixtures/                   # Test data and mocks
│       └── __init__.py
├── run_tests.py                    # Test runner script
└── TESTING.md                      # This documentation
```

## Test Categories

### Unit Tests (`tests/unit/`)

Unit tests test individual components in isolation, mocking external dependencies.

**Coverage:**
- `test_github_api_manager.py`: Tests GitHub API interaction functionality
  - Initialization with environment variables
  - Workflow disabling success and error scenarios
  - API error handling
  - Missing environment variable validation

- `test_telegram_notifier.py`: Tests Telegram notification functionality
  - Message and photo sending
  - Success notifications
  - Error notifications
  - Status updates
  - Bot initialization and error handling

### Integration Tests (`tests/integration/`)

Integration tests test component interactions and workflows, mocking external services while testing the core logic.

**Coverage:**
- `test_fliff_automator.py`: Tests browser automation functionality
  - Browser setup and configuration
  - Login workflows
  - Balance retrieval
  - Open wagers checking
  - Rewards claiming
  - Betting strategy execution
  - Odds conversion
  - Screenshot functionality
  - Error handling and cleanup

### End-to-End Tests (`tests/e2e/`)

End-to-end tests test complete application workflows with mocked dependencies.

**Coverage:**
- `test_main_orchestration.py`: Tests the main orchestrator workflow
  - Goal achievement scenarios
  - Balance checking workflows
  - Rewards claiming integration
  - Betting strategy execution
  - Error handling scenarios
  - Cleanup and resource management
  - Notification workflows

## Test Configuration

### Fixtures (`conftest.py`)

The `conftest.py` file provides shared fixtures and mock configurations:

- `mock_env_vars`: Mock environment variables for testing
- `mock_requests_get`: Mock GitHub API GET requests
- `mock_requests_put`: Mock GitHub API PUT requests
- `mock_telegram_bot`: Mock Telegram bot
- `mock_playwright`: Mock Playwright browser automation
- `sample_workflows_response`: Sample GitHub API response data
- `sample_balance_data`: Sample balance data
- `sample_games_data`: Sample games data

### Mocking Strategy

The test suite uses extensive mocking to isolate functionality:

- **External APIs**: GitHub and Telegram APIs are mocked
- **Browser Automation**: Playwright browser interactions are mocked
- **File Operations**: File operations for screenshots are mocked
- **Environment Variables**: All environment variables are mocked for consistent testing

## Dependencies

### Test Dependencies

Additional test dependencies are added to `requirements.txt`:

```
pytest==7.4.3                    # Main testing framework
pytest-cov==4.1.0                # Coverage reporting
pytest-mock==3.12.0              # Enhanced mocking capabilities
pytest-asyncio==0.21.1           # Async test support
```

### Runtime Dependencies

The application dependencies are tested as part of the integration tests:

```
playwright==1.40.0               # Browser automation
python-telegram-bot==20.7        # Telegram integration
python-dotenv==1.0.0             # Environment variable management
requests==2.31.0                 # HTTP requests
```

## Understanding Test Output

### Test Results

The test runner provides clear output:

```
============================================================
 Fliff Bot Test Suite
============================================================
Running comprehensive test suite...

----------------------------------------
 Running Unit Tests
----------------------------------------
============================= test session starts ==============================
...
collected 15 items

tests/unit/test_github_api_manager.py .......                           [ 50%]
tests/unit/test_telegram_notifier.py ........                           [100%]

============================== 15 passed in 0.12s ===============================

✅ Unit tests passed!

Coverage Report:
Name                       Stmts   Miss  Cover
---------------------------------------------
github_api_manager.py         67      0   100%
telegram_notifier.py         167      0   100%
---------------------------------------------
```

### Coverage Reports

Coverage reports show which lines of code are tested:

- **100% Coverage**: All lines in the file are tested
- **Partial Coverage**: Some lines are not tested (shown in red)
- **No Coverage**: No lines are tested

### Error Messages

Test failures provide detailed error information:

```
❌ Unit tests failed!
Error: assert False
AssertionError: Expected True but got False

tests/unit/test_github_api_manager.py:45: AssertionError
```

## Adding New Tests

### Adding Unit Tests

1. Create a new test file in `tests/unit/`
2. Follow the naming convention: `test_<module_name>.py`
3. Import necessary modules and fixtures
4. Use descriptive test method names: `test_<functionality>_<scenario>`

Example:
```python
def test_new_functionality_success(mock_env_vars):
    """Test new functionality success scenario"""
    # Test implementation
    assert result == expected_value
```

### Adding Integration Tests

1. Create a new test file in `tests/integration/`
2. Mock external dependencies while testing core logic
3. Test component interactions and workflows
4. Use the provided fixtures for consistent testing

### Adding End-to-End Tests

1. Create a new test file in `tests/e2e/`
2. Test complete application workflows
3. Mock all external dependencies
4. Test success and error scenarios

### Test Best Practices

1. **Descriptive Names**: Use clear, descriptive test names
2. **Arrange-Act-Assert**: Structure tests with setup, action, and assertion
3. **One Assertion per Test**: Focus tests on single scenarios
4. **Mock External Dependencies**: Isolate tests from external services
5. **Test Error Cases**: Include tests for failure scenarios
6. **Use Fixtures**: Leverage shared fixtures for consistency
7. **Document Tests**: Add docstrings explaining test scenarios

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```bash
# Run all tests in CI
python run_tests.py

# Run with coverage for CI
python run_tests.py && coverage xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the fliff-bot directory
2. **Missing Dependencies**: Install all requirements with `pip install -r requirements.txt`
3. **Mock Failures**: Check that all external dependencies are properly mocked
4. **Timeout Issues**: Increase timeouts in tests for slow operations

### Debugging Tests

```bash
# Run with verbose output
pytest -v

# Run with traceback
pytest --tb=long

# Run specific test with pdb
pytest -pdb tests/unit/test_github_api_manager.py::TestGitHubAPIManager::test_init_success
```

## Contributing

When contributing to the test suite:

1. Ensure all new code has corresponding tests
2. Maintain the existing test structure and conventions
3. Update this documentation when adding new test categories
4. Aim for high test coverage (target: 90%+)
5. Follow the existing mocking patterns for consistency

## Summary

The Fliff Bot test suite provides comprehensive coverage of the application through:

- **3 test categories** with different testing strategies
- **50+ test cases** covering all major functionality
- **Extensive mocking** for reliable testing
- **Coverage reporting** to ensure code quality
- **Easy execution** with a single command

Run `python run_tests.py` to verify the application is working correctly before deployment.