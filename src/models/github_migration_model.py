import os
import shutil
import csv
import json
import time
from src.configs.configurations import Configurations
from src.connectors.bitbucket_connector import BitbucketConnector
from src.connectors.github_connector import GithubConnector
from src.connectors.teamcity_connector import TeamcityConnector


class GithubMigrationModel:
    
    def __init__(self, repositories_csv_file):
        self._testing_prefix = "mock.migration."
        self._local_repo_dir = Configurations.get_git_repos_directory()
        if not all([self._local_repo_dir]):
            raise ValueError("Missing required parameters in .env file or in the exported envionment variables.")
        self._repositories = []
        self._set_repositories_list(repositories_csv_file)
        self._teamcity_project_id = Configurations.get_teamcity_project_id()
        self._repositories_string = json.dumps(self._repositories, indent=4)
        self._bitbucket_connector = BitbucketConnector()
        self._github_connector = GithubConnector()
        self._teamcity_connector = TeamcityConnector()
        self._bitbucket_repositories_vcs_roots = {}
        # self._set_bitbucket_repositories_vcs_roots()

    def _set_repositories_list(self, repositories_csv_file):
        if not os.path.exists(repositories_csv_file):
            raise FileNotFoundError(f"CSV file '{repositories_csv_file}' not found.")
        with open(repositories_csv_file, mode="r") as csv_file:
            reader = csv.DictReader(csv_file)
            if not all(col in reader.fieldnames for col in ["bitbucket_repository", "github_repository"]):
                raise ValueError("CSV file must have 'bitbucket_repository' and 'github_repository' columns.")
            for row in reader:
                respository = {}
                respository["bitbucket"] = row["bitbucket_repository"]
                respository["github"] = row["github_repository"]
                self._repositories.append(respository)
    
    def _set_bitbucket_repositories_vcs_roots(self):
        project_vcs_roots = self._teamcity_connector.generate_vcs_roots_csv(self._teamcity_project_id, None)
        for _, vcs_list in project_vcs_roots.items():
            for vcs in vcs_list:
                repo_url = self._teamcity_connector.get_vcs_root_url(vcs['href'].removeprefix("/app/rest"))
                bitbucket_base_url = self._bitbucket_connector.get_repository_base_url()
                if bitbucket_base_url in repo_url:
                    repository_name = repo_url.removeprefix(bitbucket_base_url).removesuffix(".git")
                    if not repository_name in self._bitbucket_repositories_vcs_roots:
                        self._bitbucket_repositories_vcs_roots[repository_name] = []
                    self._bitbucket_repositories_vcs_roots[repository_name].append(vcs['href'])
        return self._bitbucket_repositories_vcs_roots
    
    def _get_csv_github_repos(self):
        github_repos = []
        for repo in self._repositories:
            github_repos.append(repo['github'])
        return github_repos

    def _get_csv_bitbucket_repos(self):
        bitbucket_repos = []
        for repo in self._repositories:
            bitbucket_repos.append(repo['bitbucket'])
        return bitbucket_repos
    
    def _get_testing_github_repos(self, prefix):
        return self._github_connector.get_repos_with_prefix(prefix)
    
    def _replace_string_in_file(self, file_path, str, new_str):
        with open(file_path, "r") as file:
            file_contents = file.read()
        updated_contents = file_contents.replace(str, new_str)
        with open(file_path, "w") as file:
            file.write(updated_contents)
    
    def _replace_urls_in_file(self, file_path, bitbucket_url_1, bitbucket_url_2, github_url):
        self._replace_string_in_file(file_path, bitbucket_url_1, github_url)
        self._replace_string_in_file(file_path, bitbucket_url_2, github_url)
                
    def _get_readme_file_in_dir(self, dir):
        repo_files = os.listdir(dir)
        readme_file = ""
        for repo_file in repo_files:
            if repo_file.lower() == "readme.md":
                readme_file = repo_file
                break
        return readme_file
    
    def _delete_lines_containing_string(self, file_path, string_to_delete):
        temp_file_path = file_path + ".temp"
        try:
            with open(file_path, 'r') as source_file, open(temp_file_path, 'w') as temp_file:
                for line in source_file:
                    if string_to_delete not in line:
                        temp_file.write(line)
            os.remove(file_path)
            os.rename(temp_file_path, file_path)
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def _update_map_repo(self, repo_path, bitbucket_repo_name, github_repo_name):
        manifests_to_update = [
            "core-release.xml",
            "default.xml",
            "map-release.xml",
            "release.xml"
        ]
        scripts_to_update = [
            "release/clone_repos.sh",
            "release/create_branches.sh",
            "release/create_release_tags.sh"
        ]
        readme_file = "README.md"
        github_clone_base_url = self._github_connector.get_repository_clone_base_url()
        bitbucket_clone_base_url = self._bitbucket_connector.get_repository_clone_base_url()
        for manifest in manifests_to_update:
            manifest_path = f"{repo_path}/{manifest}"
            github_repo_tool_clone_url = github_clone_base_url.replace(":", "/")
            self._replace_string_in_file(manifest_path, bitbucket_clone_base_url, f"ssh://{github_repo_name}")
            self._replace_string_in_file(manifest_path, " fetch=\"https:", " fetch=\"ssh:")    
            if Configurations.get_ff_enable_mock_migration:
                self._delete_lines_containing_string(manifest_path, "remote=\"origin-bbc\"")
                self._delete_lines_containing_string(manifest_path, "remote=\"origin-it\"")
        for script in scripts_to_update:
            scrpit_path = f"{repo_path}/{script}"
            self._replace_string_in_file(scrpit_path, f"{bitbucket_clone_base_url}/{bitbucket_repo_name}".lower(), f"{github_clone_base_url}/{github_repo_name}".lower())
        github_org = Configurations.get_github_organization()
        self._replace_string_in_file(readme_file, f"repo init -u https://github.com/{github_org}", f"repo init -u git@github.com:/{github_org}")

    def _migrate_repository(self, repo):
        bitbucket_repo_name = repo['bitbucket']
        github_repo_name = repo['github']
        testing_github_repo_name = f"{self._testing_prefix}{github_repo_name}"
        if Configurations.get_ff_enable_mock_migration():
            github_repo_name = testing_github_repo_name
        github_repository_url = self._github_connector.get_repository_base_url() + "/" + github_repo_name
        print(f"Migrating bitbucket repo: {bitbucket_repo_name}")
        bitbucket_local_repo_path = f"{self._local_repo_dir}/{bitbucket_repo_name}"
        
        if os.path.exists(bitbucket_local_repo_path) and os.path.isdir(bitbucket_local_repo_path):
            shutil.rmtree(bitbucket_local_repo_path)
        
        print(f"Clone bitbucket repository '{bitbucket_repo_name}'...")
        self._bitbucket_connector.clone_repository(bitbucket_repo_name, bitbucket_local_repo_path)
        
        print(f"Create repository on github '{github_repo_name}'...")
        self._github_connector.create_repository_in_team(github_repo_name)
        
        print(f"Push local repository '{bitbucket_repo_name}' found in '{bitbucket_local_repo_path}' to github '{github_repo_name}' repository...")
        self._github_connector.push_repository(bitbucket_local_repo_path, github_repo_name)
        
        print(f"Removing local mirror repository: rm -rf {bitbucket_local_repo_path}...")
        if os.path.exists(bitbucket_local_repo_path) and os.path.isdir(bitbucket_local_repo_path):
            shutil.rmtree(bitbucket_local_repo_path)
        
        # migration for this repository is only code migration
        if bitbucket_repo_name == "trolley-automation":
            return
        
        if Configurations.get_ff_enable_bitbucket_set_repo_read_only() and github_repo_name:
            print(f"Set repoisotry {bitbucket_repo_name} as read only on Bitbucket...")
            self._bitbucket_connector.set_repository_read_only()
        
        if Configurations.get_ff_enable_teamcity_update_vcs_url() and bitbucket_repo_name in self._bitbucket_repositories_vcs_roots:
            for vcs_root_href in self._bitbucket_repositories_vcs_roots[bitbucket_repo_name]:
                print(f"Set git repository url to {github_repository_url} in VCS root {vcs_root_href}")
                self._teamcity_connector.update_vcs_url(vcs_root_href, github_repository_url)
            
    def print_repositories(self):
        print(self._repositories_string)
        return self._repositories_string
    
    def delete_testing_repositories_on_github(self, prefix):
        for repo in self._get_testing_github_repos(prefix):
            self._github_connector.delete_repository(repo)
            time.sleep(0.5)
    
    def delete_csv_repositories_on_github(self):
        for repo in self._get_csv_github_repos():
            self._github_connector.delete_repository(repo)
    
    def migrate_repositories(self):
        if Configurations.get_ff_cleanup_testing_repository():
            print(f"Cleanup repositories on github with prefix: '{self._testing_prefix}'...")
            self.delete_testing_repositories_on_github(self._testing_prefix)
        if not self._repositories:
            return
        print("Migragion has started")
        for repo in self._repositories:
            print("===========================")
            self._migrate_repository(repo)
            time.sleep(1)
        print("===========================")
        if Configurations.get_ff_enable_teamcity_update_commit_status_publisher():
            print(f"Update TeamCity Commit Status Publisher found in the Build Configurations in '{Configurations.get_teamcity_project_id()}' project...")
            for project, build_types in self._teamcity_connector.generate_buildtypes_csv(self._teamcity_project_id, None).items():
                print(project)
                for build_type in build_types:
                    self._teamcity_connector.update_buildtype_commit_status_publisher(build_type['id'])
        if Configurations.get_ff_enable_bitbukcet_set_project_to_read_only():
            print(f"Setting bitbucket project '{Configurations.get_bitbucket_project_key()}' to read only...")
            self._bitbucket_connector.set_project_read_only()
        print("Migragion has finished")
    
    def _update_repository_urls(self, repo):
        bitbucket_repo_name = repo['bitbucket']
        github_repo_name = repo['github']
        testing_github_repo_name = f"{self._testing_prefix}{github_repo_name}"
        if Configurations.get_ff_enable_mock_migration():
            github_repo_name = testing_github_repo_name
        # print(f"Migrating bitbucket repo: {bitbucket_repo_name}")
        github_local_repo_path = f"{self._local_repo_dir}/{github_repo_name}"
        
        if Configurations.get_ff_enable_update_urls_in_readme_file() \
        or Configurations.get_ff_enable_update_urls_in_all_files() \
        or Configurations.get_ff_enable_update_urls_in_map_repo() and bitbucket_repo_name == "map-repo":
            print(f"Removing local repository: rm -rf {github_local_repo_path}...")
            if os.path.exists(github_local_repo_path) and os.path.isdir(github_local_repo_path):
                shutil.rmtree(github_local_repo_path)
            self._github_connector.clone_repository(github_repo_name, github_local_repo_path)
        
        if not os.path.exists(github_local_repo_path) \
        or (
            os.path.exists(github_local_repo_path) \
            and not os.path.isdir(github_local_repo_path) \
        ):
            print(f"Warning Unable to find cloned GitHub repository in {github_local_repo_path}...")
            print(f"Warning: Skipping url updates in the following repository {github_repo_name}")
            return
        
        bitbucket_repo_url_1 = f"{self._bitbucket_connector.get_repository_base_url()}/{bitbucket_repo_name}".lower()
        bitbucket_repo_url_2 = f"{self._bitbucket_connector.get_repository_clone_base_url()}/{bitbucket_repo_name}".lower()
        github_repo_url = f"{self._github_connector.get_repository_base_url()}/{github_repo_name}"
        
        if Configurations.get_ff_enable_update_urls_in_readme_file():
            print(f"Update repositories urls from Bitbucket to Github in readme files in {github_local_repo_path} and pushing a new commit to github '{github_repo_name}' repo...")
            readme_file = self._get_readme_file_in_dir(github_local_repo_path)
            if readme_file:
                readme_file_path = f"{github_local_repo_path.removesuffix('/')}/{readme_file}"
                self._replace_urls_in_file(readme_file_path, bitbucket_repo_url_1, bitbucket_repo_url_2, github_repo_url)
                self._github_connector.commit_and_push_repository(github_local_repo_path)

        if Configurations.get_ff_enable_update_urls_in_map_repo() and bitbucket_repo_name.lower() == "map-repo":
            print(f"Update repositories urls from Bitbucket to Github in the release manifests...")
            self._update_map_repo(github_local_repo_path, bitbucket_repo_name, github_repo_name)
            self._github_connector.commit_and_push_repository(github_local_repo_path)
        
        if Configurations.get_ff_enable_update_urls_in_all_files():
            print(f"Update repositories urls from Bitbucket to Github in all files in {github_local_repo_path} and pushing a new commit to github '{github_repo_name}' repo...")
            print(f"Warning: Feature is not implemented yet, doing nothing...")
        
        if Configurations.get_ff_enable_update_urls_in_confluence():
            print(f"Update repositories urls in all documents in confluence...")
            print(f"Warning: Feature is not implemented yet, doing nothing...")

    def update_repositories_urls(self):
        # print("URL update has started")
        for repo in self._repositories:
            print("===========================")
            self._update_repository_urls(repo)
        print("===========================")
        # print("URL update has finished")
