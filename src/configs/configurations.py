import os
from dotenv import load_dotenv

class Configurations:
    def _get_variable_value(variable_name):
        load_dotenv()  # Load variables from .env file if present
        return os.getenv(variable_name)
    
    def debug_enabled():
        return Configurations._get_variable_value("DEBUG_ENABLED") == "1"
    
    def get_git_repos_directory():
        return Configurations._get_variable_value("GIT_REPOS_DIRECTORY")
    
    def get_teams_webhook_url():
        return Configurations._get_variable_value("TEAMS_WEBHOOK_URL")
    
    def get_bitbucket_username():
        return Configurations._get_variable_value("BITBUCKET_USERNAME")
    
    def get_bitbucket_password():
        return Configurations._get_variable_value("BITBUCKET_PASSWORD")
    
    def get_bitbucket_server_host():
        return Configurations._get_variable_value("BITBUCKET_SERVER_HOST")
    
    def get_bitbucket_clone_url():
        return Configurations._get_variable_value("BITBUCKET_CLONE_URI")
    
    def get_bitbucket_project_key():
        return Configurations._get_variable_value("BITBUCKET_PROJECT_KEY")

    def get_teamcity_token():
        return Configurations._get_variable_value("TEAMCITY_TOKEN")
    
    def get_teamcity_server_host():
        return Configurations._get_variable_value("TEAMCITY_SERVER_HOST")
    
    def get_teamcity_project_id():
        return Configurations._get_variable_value("TEAMCITY_PROJECT_ID")
    
    def get_github_api_token():
        return Configurations._get_variable_value("GITHUB_API_TOKEN")

    def get_github_organization():
        return Configurations._get_variable_value("GITHUB_ORGANIZATION")
    
    def get_github_team():
        return Configurations._get_variable_value("GITHUB_TEAM")
    
    def get_github_ssh_private_key():
        return Configurations._get_variable_value("GITHUB_SSH_PRIVATE_KEY")

    def get_ff_cleanup_testing_repository():
        return Configurations._get_variable_value("FF_CLEANUP_TESTING_REPOSITORY") == "1"

    def get_ff_enable_bitbucket_set_repo_read_only():
        return Configurations._get_variable_value("FF_ENABLE_BITBUCKET_SET_REPO_READ_ONLY") == "1"

    def get_ff_enable_teamcity_update_vcs_url():
        return Configurations._get_variable_value("FF_ENABLE_TEAMCITY_UPDATE_VCS_URL") == "1"

    def get_ff_enable_teamcity_update_commit_status_publisher():
        return Configurations._get_variable_value("FF_ENABLE_TEAMCITY_UPDATE_COMMIT_STATUS_PUBLISHER") == "1"

    def get_ff_enable_update_urls_in_readme_file():
        return Configurations._get_variable_value("FF_ENABLE_UPDATE_URLS_IN_README_FILE") == "1"

    def get_ff_enable_update_urls_in_all_files():
        return Configurations._get_variable_value("FF_ENABLE_UPDATE_URLS_IN_ALL_FILES") == "1"

    def get_ff_enable_update_urls_in_map_repo():
        return Configurations._get_variable_value("FF_ENABLE_UPDATE_URLS_IN_MAP_REPO") == "1"

    def get_ff_enable_update_urls_in_confluence():
        return Configurations._get_variable_value("FF_ENABLE_UPDATE_URLS_IN_CONFLUENCE") == "1"

    def get_ff_enable_teams_notification():
        return Configurations._get_variable_value("FF_ENABLE_TEAMS_NOTIFICATION") == "1"

    def get_ff_enable_mock_migration():
        return Configurations._get_variable_value("FF_ENABLE_MOCK_MIGRATION") == "1"

    def get_ff_enable_bitbukcet_set_project_to_read_only():
        return Configurations._get_variable_value("FF_ENABLE_BITBUKCET_SET_PROJECT_TO_READ_ONLY") == "1"

