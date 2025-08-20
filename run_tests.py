#!/usr/bin/env python3
"""
Test runner script for Fliff Bot
Run all tests with a single command: python run_tests.py
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def run_unit_tests():
    """Run unit tests"""
    print_section("Running Unit Tests")
    
    # Run unit tests with coverage
    success, stdout, stderr = run_command(
        "python -m pytest tests/unit/ -v --cov=github_api_manager --cov=telegram_notifier --cov-report=term-missing"
    )
    
    if success:
        print("✅ Unit tests passed!")
        if stdout:
            print("\nCoverage Report:")
            print(stdout)
    else:
        print("❌ Unit tests failed!")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
    
    return success


def run_integration_tests():
    """Run integration tests"""
    print_section("Running Integration Tests")
    
    # Run integration tests
    success, stdout, stderr = run_command(
        "python -m pytest tests/integration/ -v --cov=fliff_automator --cov-report=term-missing"
    )
    
    if success:
        print("✅ Integration tests passed!")
        if stdout:
            print("\nCoverage Report:")
            print(stdout)
    else:
        print("❌ Integration tests failed!")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
    
    return success


def run_e2e_tests():
    """Run end-to-end tests"""
    print_section("Running End-to-End Tests")
    
    # Run e2e tests
    success, stdout, stderr = run_command(
        "python -m pytest tests/e2e/ -v --cov=main --cov-report=term-missing"
    )
    
    if success:
        print("✅ End-to-end tests passed!")
        if stdout:
            print("\nCoverage Report:")
            print(stdout)
    else:
        print("❌ End-to-end tests failed!")
        if stderr:
            print(f"Error: {stderr}")
        if stdout:
            print(f"Output: {stdout}")
    
    return success


def run_all_tests():
    """Run all tests"""
    print_header("Fliff Bot Test Suite")
    print("Running comprehensive test suite...")
    
    results = []
    
    # Run unit tests
    unit_success = run_unit_tests()
    results.append(("Unit Tests", unit_success))
    
    # Run integration tests
    integration_success = run_integration_tests()
    results.append(("Integration Tests", integration_success))
    
    # Run e2e tests
    e2e_success = run_e2e_tests()
    results.append(("End-to-End Tests", e2e_success))
    
    # Summary
    print_header("Test Summary")
    all_passed = True
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The Fliff Bot is ready for deployment!")
    else:
        print("💥 SOME TESTS FAILED!")
        print("Please review the test output above and fix the issues.")
    print(f"{'='*60}")
    
    return all_passed


def run_specific_test_category(category):
    """Run a specific test category"""
    category = category.lower()
    
    if category == "unit":
        return run_unit_tests()
    elif category == "integration":
        return run_integration_tests()
    elif category == "e2e" or category == "end-to-end":
        return run_e2e_tests()
    else:
        print(f"Unknown test category: {category}")
        print("Available categories: unit, integration, e2e")
        return False


def show_help():
    """Show help information"""
    print_header("Fliff Bot Test Runner")
    print("Usage: python run_tests.py [options]")
    print()
    print("Options:")
    print("  [no arguments]    Run all tests (default)")
    print("  unit             Run only unit tests")
    print("  integration      Run only integration tests")
    print("  e2e              Run only end-to-end tests")
    print("  --help, -h       Show this help message")
    print()
    print("Examples:")
    print("  python run_tests.py              # Run all tests")
    print("  python run_tests.py unit         # Run only unit tests")
    print("  python run_tests.py integration  # Run only integration tests")
    print("  python run_tests.py e2e          # Run only end-to-end tests")
    print()
    print("The test suite includes:")
    print("  🧪 Unit tests: Test individual components in isolation")
    print("  🔗 Integration tests: Test component interactions")
    print("  🚀 End-to-end tests: Test complete workflows")
    print()
    print("All tests include coverage reporting and detailed output.")


def main():
    """Main function"""
    # Check if we're in the correct directory
    if not Path("fliff_automator.py").exists():
        print("Error: Please run this script from the fliff-bot directory")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h"]:
            show_help()
            return
        elif arg in ["unit", "integration", "e2e", "end-to-end"]:
            success = run_specific_test_category(arg)
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown argument: {arg}")
            show_help()
            sys.exit(1)
    
    # Run all tests by default
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()