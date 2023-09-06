import pytest
from unittest.mock import patch, mock_open

import os
import sys
# Append the path to the parent directory (project root) to sys.path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(parent_dir))

from src.connectors.github_connector import GithubConnector

@pytest.fixture
def mock_configurations(monkeypatch):
    # Mock the Configurations class to return a dummy SSH key
    def mock_get_variable_value(key):
        if key == "GITHUB_SSH_PRIVATE_KEY":
            return "dummy_key_content"
    monkeypatch.setattr("src.connectors.GithubConnector.Configurations.get_variable_value", mock_get_variable_value)

@pytest.mark.parametrize("key_exists", [True, False])
@patch("os.path.exists")
@patch("builtins.open", new_callable=mock_open, read_data="dummy_key_content")
@patch("subprocess.run")
def test_init(mock_subprocess, mock_open, mock_path_exists, key_exists, mock_configurations):
    # Mock the behavior of os.path.exists based on the parameter
    mock_path_exists.return_value = key_exists

    # Initialize GithubConnector
    github_connector = GithubConnector()

    # Assert the behavior based on whether the key exists
    if key_exists:
        # The SSH key file exists, the tool should not create it
        mock_open.assert_not_called()
        mock_subprocess.assert_not_called()
    else:
        # The SSH key file does not exist, the tool should create it
        mock_open.assert_called_with("/home/user/.ssh/id_rsa", "w")
        mock_subprocess.assert_called()
    
    assert github_connector is not None

if __name__ == "__main__":
    pytest.main()