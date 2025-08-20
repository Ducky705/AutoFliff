"""
End-to-end tests for FliffBotOrchestrator
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from main import FliffBotOrchestrator, main


class TestFliffBotOrchestrator:
    """Test cases for FliffBotOrchestrator class"""
    
    def test_init_success(self, mock_env_vars):
        """Test successful initialization"""
        orchestrator = FliffBotOrchestrator()
        
        assert orchestrator.goal_balance == 10.00
        assert orchestrator.min_bet_threshold == 1.80
        assert orchestrator.min_payout_threshold == 50.00
        assert orchestrator.max_payout_threshold == 100.00
        
        # Verify components are initialized
        assert orchestrator.automator is not None
        assert orchestrator.github_manager is not None
        assert orchestrator.telegram_notifier is not None
    
    @patch('main.FliffBotOrchestrator.run')
    def test_main_success(self, mock_run, mock_env_vars):
        """Test main function success"""
        main()
        mock_run.assert_called_once()
    
    @patch('main.FliffBotOrchestrator.run')
    @patch('sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_run, mock_env_vars):
        """Test main function with keyboard interrupt"""
        mock_run.side_effect = KeyboardInterrupt()
        main()
        mock_exit.assert_called_once_with(0)
    
    @patch('main.FliffBotOrchestrator.run')
    @patch('sys.exit')
    def test_main_exception(self, mock_exit, mock_run, mock_env_vars):
        """Test main function with exception"""
        mock_run.side_effect = Exception("Test exception")
        main()
        mock_exit.assert_called_once_with(1)
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_goal_already_met(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when goal is already met"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 15.00
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Setup github manager mock
        github_manager_instance = Mock()
        mock_github_manager.return_value = github_manager_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        automator_instance.get_balance.assert_called_once()
        notifier_instance.send_success_notification.assert_called_once_with(15.00)
        github_manager_instance.disable_workflow.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_balance_below_min_threshold(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when balance is below minimum threshold"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = [1.00, 1.00]  # Initial and after rewards
        automator_instance.check_open_wagers.return_value = False
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        automator_instance.check_and_claim_rewards.assert_called_once()
        # Should have two status updates: initial and insufficient balance
        assert notifier_instance.send_status_update.call_count == 2
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_balance_below_min_threshold_after_rewards(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when balance is still below minimum after claiming rewards"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = [1.00, 0.50]  # Initial and after rewards
        automator_instance.check_open_wagers.return_value = False
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        automator_instance.check_and_claim_rewards.assert_called_once()
        # Should have two status updates: initial and insufficient balance
        assert notifier_instance.send_status_update.call_count == 2
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_balance_sufficient_for_betting(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when balance is sufficient for betting"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = [5.00, 5.00]  # Initial and final balance
        automator_instance.check_open_wagers.return_value = False
        automator_instance.execute_betting_strategy.return_value = True
        automator_instance.get_current_payout.return_value = 75.00
        automator_instance.take_bet_screenshot.return_value = "test_screenshot.png"
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        automator_instance.execute_betting_strategy.assert_called_once_with(
            min_payout=50.00,
            max_payout=100.00
        )
        notifier_instance.send_bet_confirmation.assert_called_once_with(
            wager_amount=5.00,
            potential_potential_payout=75.00,
            screenshot_path="test_screenshot.png"
        )
        automator_instance.take_bet_screenshot.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_no_suitable_parlay(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when no suitable parlay can be constructed"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = [5.00, 5.00]  # Initial and final balance
        automator_instance.check_open_wagers.return_value = False
        automator_instance.execute_betting_strategy.return_value = False
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        # Should have two status updates: initial and no suitable parlay
        assert notifier_instance.send_status_update.call_count == 2
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_with_blocking_wagers(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when there are blocking wagers"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 5.00
        automator_instance.check_open_wagers.return_value = True
        mock_automator.return_value = automator_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify no betting was attempted
        automator_instance.execute_betting_strategy.assert_not_called()
        # Should have initial status update
        mock_telegram_notifier.return_value.send_status_update.assert_called_with("Bot started execution")
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_with_exception(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test run when an exception occurs"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = Exception("Test exception")
        automator_instance.take_error_screenshot.return_value = "error_screenshot.png"
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify behavior
        notifier_instance.send_error_notification.assert_called_once_with(
            "Test exception",
            "error_screenshot.png"
        )
        automator_instance.take_error_screenshot.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_cleanup_always_called(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test that cleanup is always called"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 15.00
        mock_automator.return_value = automator_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify cleanup was called
        automator_instance.close.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_cleanup_with_exception(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test that cleanup is called even when an exception occurs during cleanup"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.side_effect = Exception("Test exception")
        automator_instance.take_error_screenshot.return_value = "error_screenshot.png"
        automator_instance.close.side_effect = Exception("Cleanup failed")
        mock_automator.return_value = automator_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify cleanup was attempted despite exception
        automator_instance.close.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_screenshot_cleanup(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars, tmp_path):
        """Test that screenshots are cleaned up after execution"""
        # Setup automator mock
        screenshot_path = str(tmp_path / "test_screenshot.png")
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 5.00
        automator_instance.check_open_wagers.return_value = False
        automator_instance.execute_betting_strategy.return_value = True
        automator_instance.get_current_payout.return_value = 75.00
        automator_instance.take_bet_screenshot.return_value = screenshot_path
        mock_automator.return_value = automator_instance
        
        # Create the screenshot file
        screenshot_file = tmp_path / "test_screenshot.png"
        screenshot_file.write_text("fake screenshot")
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify screenshot file was cleaned up
        assert not screenshot_file.exists()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_screenshot_cleanup_file_not_found(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test that cleanup handles missing screenshot files gracefully"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 5.00
        automator_instance.check_open_wagers.return_value = False
        automator_instance.execute_betting_strategy.return_value = True
        automator_instance.get_current_payout.return_value = 75.00
        automator_instance.take_bet_screenshot.return_value = "nonexistent_screenshot.png"
        mock_automator.return_value = automator_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify cleanup was attempted without error
        automator_instance.close.assert_called_once()
    
    @patch('main.TelegramNotifier')
    @patch('main.GitHubAPIManager')
    @patch('main.FliffAutomator')
    def test_run_initial_status_update(self, mock_automator, mock_github_manager, mock_telegram_notifier, mock_env_vars):
        """Test that initial status update is sent"""
        # Setup automator mock
        automator_instance = Mock()
        automator_instance.get_balance.return_value = 5.00
        automator_instance.check_open_wagers.return_value = False
        automator_instance.execute_betting_strategy.return_value = True
        automator_instance.get_current_payout.return_value = 75.00
        automator_instance.take_bet_screenshot.return_value = "test_screenshot.png"
        mock_automator.return_value = automator_instance
        
        # Setup notifier mock
        notifier_instance = Mock()
        mock_telegram_notifier.return_value = notifier_instance
        
        # Create orchestrator and run
        orchestrator = FliffBotOrchestrator()
        orchestrator.run()
        
        # Verify initial status update was sent
        notifier_instance.send_status_update.assert_called_with("Bot started execution")
    
    def test_goal_balance_property(self, mock_env_vars):
        """Test goal_balance property"""
        orchestrator = FliffBotOrchestrator()
        assert orchestrator.goal_balance == 10.00
    
    def test_min_bet_threshold_property(self, mock_env_vars):
        """Test min_bet_threshold property"""
        orchestrator = FliffBotOrchestrator()
        assert orchestrator.min_bet_threshold == 1.80
    
    def test_min_payout_threshold_property(self, mock_env_vars):
        """Test min_payout_threshold property"""
        orchestrator = FliffBotOrchestrator()
        assert orchestrator.min_payout_threshold == 50.00
    
    def test_max_payout_threshold_property(self, mock_env_vars):
        """Test max_payout_threshold property"""
        orchestrator = FliffBotOrchestrator()
        assert orchestrator.max_payout_threshold == 100.00