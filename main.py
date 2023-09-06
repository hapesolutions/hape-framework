import os
import json
from src.configs.configurations import Configurations
from src.connectors.bitbucket_connector import BitbucketConnector
from src.connectors.teamcity_connector import TeamcityConnector
from src.connectors.github_connector import GithubConnector
from src.connectors.teams_connector import TeamsConnector
from src.models.github_migration_model import GithubMigrationModel


CSV_FILES_DIRECTORY = "./csv"

def generate_bitbucket_repositories_csv(output_csv_file_path):
    bitbucket_connector = BitbucketConnector()
    bitbucket_connector.generate_repository_list_csv(output_csv_file_path)
    
def set_bitbucket_repository_to_read_only(repo_name):
    bitbucket_connector = BitbucketConnector()
    bitbucket_connector.set_repository_read_only(repo_name)
  
def set_bitbucket_project_to_read_only():
    bitbucket_connector = BitbucketConnector()
    bitbucket_connector.set_project_read_only()
    
def generate_teamcity_vcsroot_csv(project_id, output_csv_file_path):
    teamcity_connector = TeamcityConnector()
    teamcity_connector.generate_vcs_roots_csv(project_id, output_csv_file_path)
    
def update_teamcity_vcs_root(vcs_href, new_url):
    teamcity_connector = TeamcityConnector()
    teamcity_connector.update_vcs_url(vcs_href, new_url)
    
def create_github_repo_in_team(repo_name):
    github_connector = GithubConnector()
    github_connector.create_repository_in_team(repo_name)
    
def update_buildtype_commit_status_publisher(buildtype_id):
    teamcity_connector = TeamcityConnector()
    teamcity_connector.update_buildtype_commit_status_publisher(buildtype_id)

def generate_teamcity_buildtype_csv(project_id, output_csv_file_path):
    teamcity_connector = TeamcityConnector()
    teamcity_connector.generate_buildtypes_csv(project_id, output_csv_file_path)

def send_teams_success_message(message, details):
    teams_connector = TeamsConnector()
    teams_connector.send_success_message(message=message, details=details)

def send_teams_failure_message(message, details):
    teams_connector = TeamsConnector()
    teams_connector.send_failure_message(message=message, details=details)

def send_teams_info_message(message, details):
    teams_connector = TeamsConnector()
    teams_connector.send_info_message(message=message, details=details)
    
def migrate_repositories(input_csv_file_path):
    github_migrator = GithubMigrationModel(input_csv_file_path)
    github_migrator.print_repositories()
    github_migrator.migrate_repositories()

def generate_open_pull_requests_in_bitbucket_csv(output_csv_file_path):
    bitbucket_connector = BitbucketConnector()
    bitbucket_connector.generate_open_pull_requests_csv(output_csv_file_path)
    
def delete_repository_in_github(repo_name):
    github_connector = GithubConnector()
    github_connector.delete_repository(repo_name)
    
def delete_csv_repositories_on_github(repositories_csv_file):
    github_migrator = GithubMigrationModel(repositories_csv_file)
    github_migrator.delete_csv_repositories_on_github()
    
def delete_testing_repositories_on_github(repositories_csv_file, prefix):
    github_migrator = GithubMigrationModel(repositories_csv_file)
    github_migrator.delete_testing_repositories_on_github(prefix)

def main_functionality():
    if not os.path.exists(CSV_FILES_DIRECTORY):
        os.makedirs(CSV_FILES_DIRECTORY)
    
    # # ===================================================================
    # output_csv_file_path = f"{CSV_FILES_DIRECTORY}/output_repositories.csv"
    # generate_bitbucket_repositories_csv(output_csv_file_path)
    
    # # ===================================================================
    # repo_name = "hazem_test"
    # set_bitbucket_repository_to_read_only(repo_name)
    
    # # ===================================================================
    # project_id = "Mapping_Playground"
    # output_csv_file_path = f"{CSV_FILES_DIRECTORY}/vcs_roots.csv"
    # generate_teamcity_vcsroot_csv(project_id, output_csv_file_path)
    
    # # ===================================================================
    # vcs_href = "/app/rest/vcs-roots/id:Mapping_Playground_MapTestRepo"
    # new_url = "https://github.com/org/repo.map.test.migration"
    # update_teamcity_vcs_root(vcs_href, new_url)
    
    # # ===================================================================
    # buildtype_id = ""
    # update_buildtype_commit_status_publisher(buildtype_id)
    
    # # ===================================================================
    # project_id = "Mapping_Playground"
    # output_csv_file_path = f"{CSV_FILES_DIRECTORY}/buildtypes.csv"
    # generate_teamcity_buildtype_csv(project_id, output_csv_file_path)
    
    # # ===================================================================
    # repo_name = ""
    # ssh_key_path = "/root/.ssh/id_rsa"
    # if os.path.exists(ssh_key_path):
    #     os.remove("/root/.ssh/id_rsa")
    # create_github_repo_in_team(repo_name)
    
    # # ===================================================================
    # message = "We have done it!"
    # details = "well, everything seems fine"
    # send_teams_success_message(message, details)
    
    # # ===================================================================
    # message = "Something went wrong"
    # details = "some error in some place has happened"
    # send_teams_failure_message(message, details)
    
    # # ===================================================================
    # message = "This is information message"
    # details = "make sure to read the details of an information message"
    # send_teams_info_message(message, details)
    
    # ===================================================================
    input_csv_file_path = f"{CSV_FILES_DIRECTORY}/repositories.csv"
    migrate_repositories(input_csv_file_path)
    
    # # ===================================================================
    # output_csv_file_path = f"{CSV_FILES_DIRECTORY}/open_pull_requests.csv"
    # generate_open_pull_requests_in_bitbucket_csv(output_csv_file_path)
    
    # # ===================================================================
    # repo_name = ""
    # delete_repository_in_github(repo_name)
    
    # =====================================================================
    # input_csv_file_path = f"{CSV_FILES_DIRECTORY}/repositories.csv"
    # delete_csv_repositories_on_github(input_csv_file_path)
    
    # # ===================================================================
    # input_csv_file_path = f"{CSV_FILES_DIRECTORY}/repositories.csv"
    # prefix = ""
    # delete_testing_repositories_on_github(input_csv_file_path, prefix)
    
    # # ===================================================================
    # input_csv_file_path = f"{CSV_FILES_DIRECTORY}/repositories.csv"
    # get_bitbucket_repositories_vcs_roots(input_csv_file_path)
    
    # =====================================================================
    pass

def main():
    if Configurations.debug_enabled():
        main_functionality()
    else:
        try:    
            main_functionality()
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
    
if __name__ == "__main__":
    main()