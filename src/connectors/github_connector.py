import os
import shutil
import time
import subprocess
import requests
import json
from src.configs.configurations import Configurations

class GithubConnector:

    def __init__(
            self,
            api_token=None,
            organization=None,
            team=None
        ):
        self._github_api_token = api_token if api_token else Configurations.get_github_api_token()
        self._github_organization = organization if organization else Configurations.get_github_organization()
        self._github_team = team if team else Configurations.get_github_team()
        self._github_api_base_url = "https://api.github.com"
        if not all([self._github_api_token, self._github_organization,  self._github_team]):
            raise ValueError("Missing required parameters in .env file or in the exported envionment variables.")
        
        github_ssh_key = Configurations.get_github_ssh_private_key()
        home_directory = os.path.expanduser("~")
        self.ssh_key_path = f"{home_directory}/.ssh/id_rsa"

        try:
            if os.path.exists(self.ssh_key_path):
                print(f"Warning: SSH key file {self.ssh_key_path} already exists.")
            else:    
                os.makedirs(os.path.dirname(self.ssh_key_path), exist_ok=True)
                with open(self.ssh_key_path, "w") as file:
                    file.write(github_ssh_key)
                subprocess.run(["chmod", "0600", self.ssh_key_path])
                print("SSH key written successfully.")

                result = subprocess.run(["ssh-keyscan", "github.com"], capture_output=True, text=True, check=True)
                public_key = result.stdout.strip()
                with open(os.path.expanduser("~/.ssh/known_hosts"), "a") as known_hosts_file:
                    known_hosts_file.write(public_key + "\n")
                print("Host added to known_hosts file successfully.")

        except Exception as e:
            print(f"Error writing GitHub SSH key: {e}")
            exit(1)
            
    def get_repository_base_url(self):
        return f"https://github.com/{self._github_organization}".removesuffix('/')
    
    def get_repository_clone_base_url(self):
        return f"git@github.com:{self._github_organization}"
    
    def _backup_ssh_key(self):
        ssh_dir = os.path.expanduser("~/.ssh")
        rsa_key_path = os.path.join(ssh_dir, "id_rsa")

        if os.path.exists(rsa_key_path):
            timestamp = int(time.time())
            backup_key_path = os.path.join(ssh_dir, f"id_rsa_{timestamp}")

            try:
                shutil.move(rsa_key_path, backup_key_path)
                print(f"Backup: Moved {rsa_key_path} to {backup_key_path}")
            except Exception as e:
                print(f"Error moving SSH key: {e}")
            return backup_key_path
        else:
            print(f"No SSH key found at {rsa_key_path}")
        return ""
            
    def _execute_github_command(self, uri, method="GET", data=None):
        headers = {
            "Authorization": f"Bearer {self._github_api_token}",
            "Content-Type": "application/json",
        }
        url = f"{self._github_api_base_url}{uri}"
        response = None

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, data=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError('Request method not supported in code')
            response.raise_for_status()        
            return response.json() if response.text else {}
        
        except requests.exceptions.RequestException as e:
            print(f"Error executing Github command: {e}")
            exit(1)
            
    def _execute_git_command(self, command_list, repo_path=""):
        if repo_path:
            os.chdir(repo_path)
        command = " ".join(command_list)
        result = subprocess.run(
            command_list,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            print(f"Git command '{command}' succeeded")
        else:
            print(f"Git command '{command}' failed")
        return result
    
    def _get_repo(self, repo_name):
        uri = f"/repos/{self._github_organization}/{repo_name}"
        return self._execute_bitbucket_command(uri, method="GET")
    
    def get_repos_with_prefix(self, prefix):
        uri = f"/orgs/{self._github_organization}/repos?type=private&&per-page=100"
        response = self._execute_github_command(uri, method="GET")
        testing_repos = []
        for repo in response:
            repo_name = repo.get("name")
            if repo_name.startswith(prefix):
                testing_repos.append(repo_name)
        return testing_repos

    def _create_repo(self, repo_name):
        uri = f"/orgs/{self._github_organization}/repos"
        body = {
            "name": repo_name,
            "homepage": "https://github.com",
            "private": True
        }
        return self._execute_github_command(uri, method="POST", data=body)

    def _add_repo_to_team(self, repo_name):
        uri = f"/orgs/{self._github_organization}/teams/{self._github_team}/repos/{self._github_organization}/{repo_name}"
        body = {
                "permission": "push"
            }
        return self._execute_github_command(uri, method="PUT", data=body)

    def clone_repository(self, repo_name, local_repo_path):
            if os.path.exists(local_repo_path):
                try:
                    shutil.rmtree(local_repo_path)
                except Exception as e:
                    print(f"Error while deleting exiting repository in {local_repo_path}: {e}")
                    exit(1)
            repo_url = f"git@github.com:{self._github_organization}/{repo_name}.git"
            result = self._execute_git_command(["git", "clone", repo_url, local_repo_path])
            if result.returncode == 0:
                print(f"Repository '{repo_name}' cloned successfully from GitHub.")
            else:
                print(f"Cloning '{repo_name}' from GitHub has failed")
                
    def commit_and_push_repository(self, local_repo_path):
        unable_to_commit_and_push_message = f"Warning: Unable to commit and push repository in {local_repo_path}"
        if not os.path.exists(local_repo_path):
            print(unable_to_commit_and_push_message)
            return
        result = self._execute_git_command(["git", "add", "."], local_repo_path)
        if result.returncode != 0:
            print(unable_to_commit_and_push_message)
            return
        commit_message = "Update bitbucket urls to github urls in readme file"
        try:
            result = self._execute_git_command(["git", "commit", "-m", commit_message], local_repo_path)
            return_code = result.returncode
        except Exception as e:
            print(f"Warning: Git commit command has failed, probably because there is nothing to commit")
            return_code = 1
        if return_code != 0:
            print(unable_to_commit_and_push_message)
            return
        result = self._execute_git_command(['git', 'branch', '--show-current'], local_repo_path)
        if result.returncode != 0:
            print(unable_to_commit_and_push_message)
            return
        current_branch = result.stdout.strip()
        result = self._execute_git_command(["git", "push", "origin", current_branch], local_repo_path)
        if result.returncode != 0:
            print(unable_to_commit_and_push_message)
            return
        
    def delete_repository(self, repo_name):
        uri = f"/repos/{self._github_organization}/{repo_name}"
        return self._execute_github_command(uri, method="DELETE")
    
    def push_repository(self, local_repo_path, repo_name):
        if os.path.exists(local_repo_path):
            print(f"Repository '{repo_name}' already exists. Skipping clone.")
            return False
        github_repo_url = f"git@github.com:{self._github_organization}/{repo_name}.git"
        os.chdir(local_repo_path)
        subprocess.run(["git", "remote", "add", "github", github_repo_url])
        subprocess.run(["git", "push", "github", "--all"])
        subprocess.run(["git", "push", "github", "--tags"])
        print("Repository pushed to GitHub successfully.")

    def create_repository_in_team(self, repo_name):
        self._create_repo(repo_name)
        self._add_repo_to_team(repo_name)

