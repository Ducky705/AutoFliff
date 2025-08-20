"""
Unit tests for GitHubAPIManager
"""
import pytest
import os
import requests
from unittest.mock import Mock, patch, mock_open
from github_api_manager import GitHubAPIManager


class TestGitHubAPIManager:
    """Test cases for GitHubAPIManager class"""
    
    def test_init_success(self, mock_env_vars):
        """Test successful initialization with proper environment variables"""
        manager = GitHubAPIManager()
        
        assert manager.github_token == 'test_github_token'
        assert manager.github_repository == 'test/test-repo'
        assert manager.workflow_filename == 'main.yml'
    
    def test_init_missing_github_token(self):
        """Test initialization failure when GITHUB_TOKEN is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
                GitHubAPIManager()
    
    def test_init_missing_github_repository(self, mock_env_vars):
        """Test initialization failure when GITHUB_REPOSITORY is missing"""
        # Use fresh environment without GITHUB_REPOSITORY
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}, clear=True):
            with pytest.raises(ValueError, match="GITHUB_REPOSITORY environment variable is required"):
                GitHubAPIManager()
    
    @patch('github_api_manager.requests.get')
    @patch('github_api_manager.requests.put')
    def test_disable_workflow_success(self, mock_put, mock_get, mock_env_vars, sample_workflows_response):
        """Test successful workflow disabling"""
        # Mock successful API responses
        mock_get_response = Mock()
        mock_get_response.json.return_value = sample_workflows_response
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        mock_put_response = Mock()
        mock_put_response.raise_for_status.return_value = None
        mock_put.return_value = mock_put_response
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is True
        
        # Verify API calls were made correctly
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/test/test-repo/actions/workflows",
            headers={
                'Authorization': 'token test_github_token',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
        
        mock_put.assert_called_once_with(
            "https://api.github.com/repos/test/test-repo/actions/workflows/12345/disable",
            headers={
                'Authorization': 'token test_github_token',
                'Accept': 'application/vnd.github.v3+json'
            }
        )
    
    @patch('github_api_manager.requests.get')
    def test_disable_workflow_no_workflows(self, mock_get, mock_env_vars):
        """Test workflow disabling when no workflows are found"""
        # Mock empty response
        mock_get_response = Mock()
        mock_get_response.json.return_value = {'workflows': []}
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
        mock_get.assert_called_once()
    
    @patch('github_api_manager.requests.get')
    def test_disable_workflow_not_found(self, mock_get, mock_env_vars):
        """Test workflow disabling when target workflow is not found"""
        # Mock response with different workflow
        mock_get_response = Mock()
        mock_get_response.json.return_value = {
            'workflows': [
                {
                    'id': 67890,
                    'path': '.github/workflows/other.yml',
                    'state': 'active'
                }
            ]
        }
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
        mock_get.assert_called_once()
    
    @patch('github_api_manager.requests.get')
    def test_disable_workflow_get_request_fails(self, mock_get, mock_env_vars):
        """Test workflow disabling when GET request fails"""
        # Mock failed request
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
    
    @patch('github_api_manager.requests.get')
    @patch('github_api_manager.requests.put')
    def test_disable_workflow_put_request_fails(self, mock_put, mock_get, mock_env_vars, sample_workflows_response):
        """Test workflow disabling when PUT request fails"""
        # Mock successful GET but failed PUT
        mock_get_response = Mock()
        mock_get_response.json.return_value = sample_workflows_response
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        mock_put.side_effect = requests.exceptions.RequestException("Network error")
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
    
    @patch('github_api_manager.requests.get')
    def test_disable_workflow_api_error(self, mock_get, mock_env_vars):
        """Test workflow disabling when API returns an error"""
        # Mock API error response
        mock_get_response = Mock()
        mock_get_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_get_response
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
    
    @patch('github_api_manager.requests.get')
    @patch('github_api_manager.requests.put')
    def test_disable_workflow_unexpected_error(self, mock_put, mock_get, mock_env_vars, sample_workflows_response):
        """Test workflow disabling when unexpected error occurs"""
        # Mock successful GET but unexpected error during processing
        mock_get_response = Mock()
        mock_get_response.json.return_value = sample_workflows_response
        mock_get_response.raise_for_status.return_value = None
        mock_get.return_value = mock_get_response
        
        # Simulate unexpected error
        mock_put.side_effect = Exception("Unexpected error")
        
        manager = GitHubAPIManager()
        result = manager.disable_workflow()
        
        assert result is False
    
    def test_workflow_filename_property(self, mock_env_vars):
        """Test workflow_filename property"""
        manager = GitHubAPIManager()
        assert manager.workflow_filename == 'main.yml'
    
    def test_github_token_property(self, mock_env_vars):
        """Test github_token property"""
        manager = GitHubAPIManager()
        assert manager.github_token == 'test_github_token'
    
    def test_github_repository_property(self, mock_env_vars):
        """Test github_repository property"""
        manager = GitHubAPIManager()
        assert manager.github_repository == 'test/test-repo'