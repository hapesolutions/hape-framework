import os
import json
import base64
import shutil
import subprocess
from datetime import datetime
import csv
import requests
from src.configs.configurations import Configurations

class BitbucketConnector:
    
    REPO_READ_ONLY_PERMISSION = "REPO_READ"
    PROJECT_READ_ONLY_PERMISSION = "PROJECT_READ"
    
    def __init__(
            self, 
            username=None, 
            password=None, 
            server_host=None, 
            clone_uri=None, 
            project_key=None
        ):
        self._username = username if username else Configurations.get_bitbucket_username()
        self._password = password if password else Configurations.get_bitbucket_password()
        self._server_host = server_host if server_host else Configurations.get_bitbucket_server_host()
        self._clone_uri = clone_uri if clone_uri else Configurations.get_bitbucket_clone_url()
        self._project_key = project_key if project_key else Configurations.get_bitbucket_project_key()
        if not all([self._username, self._password, self._server_host]):
            raise ValueError("Missing required parameters in .env file or in the exported envionment variables.")
        self.base_url_repos = f"https://{self._server_host}/rest/api/latest"
        
    def get_repository_base_url(self):
        return f"https://{self._server_host}/projects/{self._project_key}/repos".removesuffix('/')

    def get_repository_clone_base_url(self):
        return f"https://{self._server_host}{self._clone_uri}".removesuffix('/')

    def _execute_bitbucket_command(self, uri, method="GET", data=None):
        auth_string = base64.b64encode(f"{self._username}:{self._password}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url_repos}{uri}"
        response = None
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, data=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            elif method == "PUT":
                response = requests.put(url, headers=headers)
            else:
                raise ValueError('Request method not supported in code')

            response.raise_for_status()        
            return response.json() if response.text else {}
        
        except requests.exceptions.RequestException as e:
            print(f"Error executing Bitbucket command: {e}")
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
    
    def _get_repository_list(self):
        uri = f"/projects/{self._project_key}/repos?limit=1000"
        response = self._execute_bitbucket_command(uri)
        repositories = response.get("values", [])
        return repositories
    
    def _get_groups_list(self, uri):
        groups = []
        groups_response = self._execute_bitbucket_command(uri)
        group_list = groups_response.get("values", [])
        for group in group_list:
            if "group" in group and "name" in group["group"]:
                groups.append(group["group"])
        return groups
    
    def _get_users_list(self, uri):
        users = []
        users_response = self._execute_bitbucket_command(uri)
        user_list = users_response.get("values", [])
        for user in user_list:
            if "user" in user and "name" in user["user"]:
                users.append(user["user"])
        return users
    
    def _get_repo_access_groups_list(self, repo_name):
        uri = f"/projects/{self._project_key}/repos/{repo_name}/permissions/groups"
        return self._get_groups_list(uri)
    
    def _set_repo_group_access_read_only(self, repo_name, group_name):
        uri = f"/projects/{self._project_key}/repos/{repo_name}/permissions/groups?name={group_name}&permission={BitbucketConnector.REPO_READ_ONLY_PERMISSION}"
        self._execute_bitbucket_command(uri, method="PUT")
    
    def _get_repo_access_users_list(self, repo_name):
        uri = f"/projects/{self._project_key}/repos/{repo_name}/permissions/users"
        return self._get_users_list(uri)
                
    def _set_repo_user_access_read_only(self, repo_name, user_name):
        uri = f"/projects/{self._project_key}/repos/{repo_name}/permissions/users?name={user_name}&permission={BitbucketConnector.REPO_READ_ONLY_PERMISSION}"
        self._execute_bitbucket_command(uri, method="PUT")
        
    def _get_project_access_groups_list(self):
        uri = f"/projects/{self._project_key}/permissions/groups"
        return self._get_groups_list(uri)
    
    def _set_project_group_access_read_only(self, group_name):
        uri = f"/projects/{self._project_key}/permissions/groups?name={group_name}&permission={BitbucketConnector.PROJECT_READ_ONLY_PERMISSION}"
        self._execute_bitbucket_command(uri, method="PUT")
    
    def _get_project_access_users_list(self):
        uri = f"/projects/{self._project_key}/permissions/users"
        return self._get_users_list(uri)
                
    def _set_project_user_access_read_only(self, user_name):
        uri = f"/projects/{self._project_key}/permissions/users?name={user_name}&permission={BitbucketConnector.PROJECT_READ_ONLY_PERMISSION}"
        self._execute_bitbucket_command(uri, method="PUT")
        
    def _get_open_pull_requests(self, repo_name):
        uri = f"/projects/{self._project_key}/repos/{repo_name}/pull-requests?state=OPEN&limit=1000"
        response = self._execute_bitbucket_command(uri)
        pull_requests = response.get("values", [])
        return pull_requests

    def generate_repository_list_csv(self, csv_file_path):
        try:
            repositories = self._get_repository_list()
            with open(csv_file_path, mode="w", newline='') as csv_file:
                fieldnames = ["bitbucket_repository", "github_repository"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for repo in repositories:
                    writer.writerow({
                        "bitbucket_repository": repo["name"],
                        "github_repository": repo["name"]
                    })
            print(f"Repository list saved to '{csv_file_path}'")
        except Exception as e:
            print(f"Error: {e}")
            
    import datetime

    def generate_open_pull_requests_csv(self, csv_file_path):
        try:
            repositories = self._get_repository_list()
            with open(csv_file_path, mode="w", newline='') as csv_file:
                fieldnames = [
                        "pull_request_repository",
                        "pull_request_author_name",
                        "pull_request_author_email",
                        "pull_request_author_id",
                        "pull_request_title",
                        "pull_request_number",
                        "pull_request_url",
                        "pull_request_created_at",
                        "pull_request_updated_at",
                        "pull_request_source_branch",
                        "pull_request_target_branch",
                        "pull_request_reviewers",
                        "pull_request_comments_count",
                        "pull_request_open_task_count"
                    ]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for repository in repositories:
                    pull_requests = self._get_open_pull_requests(repository["name"])
                    for pull_request in pull_requests:
                        created_at = datetime.fromtimestamp(pull_request["createdDate"]/1000).strftime("%Y.%m.%d %H:%M:%S")
                        updated_at = datetime.fromtimestamp(pull_request["updatedDate"]/1000).strftime("%Y.%m.%d %H:%M:%S")
                        reviewers = []
                        for reviewer in pull_request["reviewers"]:
                            reviewers.append(reviewer["user"]["displayName"])
                        writer.writerow({
                            "pull_request_repository": repository["name"],
                            "pull_request_author_name": pull_request["author"]["user"]["displayName"],
                            "pull_request_author_email": pull_request["author"]["user"]["emailAddress"],
                            "pull_request_author_id": pull_request["author"]["user"]["name"],
                            "pull_request_title": pull_request["title"],
                            "pull_request_number": pull_request["id"],
                            "pull_request_url": pull_request["links"]["self"][0]["href"],
                            "pull_request_created_at": created_at,
                            "pull_request_updated_at": updated_at,
                            "pull_request_source_branch": pull_request["fromRef"]["displayId"],
                            "pull_request_target_branch": pull_request["toRef"]["displayId"],
                            "pull_request_reviewers": " - ".join(reviewers),
                            "pull_request_comments_count": pull_request["properties"]["commentCount"] if "commentCount" in pull_request["properties"] else 0,
                            "pull_request_open_task_count": pull_request["properties"]["openTaskCount"] if "openTaskCount" in pull_request["properties"] else 0
                        })
            print(f"Open pull requests list saved to '{csv_file_path}'")
        except Exception as e:
            print(f"Error: {e}")

    def clone_repository(self, repo_name, local_repo_path):
        if os.path.exists(local_repo_path):
            try:
                shutil.rmtree(local_repo_path)
            except Exception as e:
                print(f"Error while deleting exiting repository in {local_repo_path}: {e}")
                exit(1)
        repo_url = f"https://{self._username}:{self._password}@{self._server_host}{self._clone_uri}{repo_name}.git"
        result = subprocess.run(
            ["git", "clone", "--mirror", repo_url, local_repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  
        )
        if result.returncode == 0:
            print(f"Repository '{repo_name}' cloned successfully from Bitbucket.")
        else:
            print(f"Cloning '{repo_name}' from Bitbucket has failed")

    def set_repository_read_only(self, repo_name):
        try:
            groups = self._get_repo_access_groups_list(repo_name)
            for group in groups:
                self._set_repo_group_access_read_only(repo_name, group["name"])
            users = self._get_repo_access_users_list(repo_name)
            for user in users:
                self._set_repo_user_access_read_only(repo_name, user["name"])
            print(f"Repository '{repo_name}' has been set to read-only for all groups and users.")
        except Exception as e:
            print(f"Error setting repository read-only: {e}")

    def set_project_read_only(self):
        try:
            groups = self._get_project_access_groups_list()
            for group in groups:
                self._set_project_group_access_read_only(group["name"])
            users = self._get_project_access_users_list()
            for user in users:
                self._set_project_user_access_read_only(user["name"])
            print(f"Project {self._project_key} has been set to read-only for all groups and users.")
        except Exception as e:
            print(f"Error setting project read-only: {e}")
