import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GitHubAPIManager:
    """Manages interactions with the GitHub API for workflow control."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repository = os.getenv('GITHUB_REPOSITORY')
        self.workflow_filename = 'main.yml'
        
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        if not self.github_repository:
            raise ValueError("GITHUB_REPOSITORY environment variable is required")
    
    def disable_workflow(self) -> bool:
        """
        Disable the GitHub Actions workflow to prevent future scheduled runs.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get workflow ID from the workflow filename
            workflows_url = f"https://api.github.com/repos/{self.github_repository}/actions/workflows"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get all workflows to find our workflow
            response = requests.get(workflows_url, headers=headers)
            response.raise_for_status()
            
            workflows = response.json().get('workflows', [])
            target_workflow = None
            
            for workflow in workflows:
                if workflow.get('path') == f'.github/workflows/{self.workflow_filename}':
                    target_workflow = workflow
                    break
            
            if not target_workflow:
                logger.error(f"Workflow '{self.workflow_filename}' not found")
                return False
            
            workflow_id = target_workflow['id']
            
            # Disable the workflow
            disable_url = f"https://api.github.com/repos/{self.github_repository}/actions/workflows/{workflow_id}/disable"
            response = requests.put(disable_url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Successfully disabled workflow: {self.workflow_filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to disable workflow: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error disabling workflow: {e}")
            return False