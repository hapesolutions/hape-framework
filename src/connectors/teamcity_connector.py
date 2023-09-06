import json
import csv
import requests
from src.configs.configurations import Configurations

class TeamcityConnector:
    
    def __init__(
            self,
            token=None,
            server_host=None,
            bitbucket_server_host=None
        ):
        self._token = token if token else Configurations.get_teamcity_token()
        self._server_host = server_host if server_host else Configurations.get_teamcity_server_host()
        self._base_url = f"https://{self._server_host}/app/rest"
        self._bitbucket_server_host = bitbucket_server_host if bitbucket_server_host else Configurations.get_teamcity_server_host()
        self._teamcity_project_id = Configurations.get_teamcity_project_id()
        if not all([self._token, self._server_host]):
            raise ValueError("Missing required parameters in .env file or in the exported envionment variables.")

    def _execute_teamcity_command(self, uri, method="GET", data=None, is_text=False):
        headers = {
            "Authorization": f"Bearer {self._token}"
        }
        if is_text:
            headers["Content-Type"] = "text/plain"
            headers["Accept"] = "text/plain"
        else:
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
        url = f"{self._base_url}{uri}"
        response = None
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "PUT":
                if is_text:
                    response = requests.put(url, headers=headers, data=data)
                else:
                    response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError('Request method not supported in code')
            response.raise_for_status()
            if is_text:
                return response.text
            else:
                return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"Error executing TeamCity command: {e}")
            exit(1)
            
    def _get_sub_projects(self, project_id):
        uri = f"/projects/id:{project_id}?fields=projects(*)"
        subprojects = self._execute_teamcity_command(uri, method="GET")
        if "projects" in subprojects and "project" in subprojects["projects"]:
            return subprojects["projects"]["project"]
        return []
    
    def _get_project_buildtypes(self, project_id):
        uri = f"/projects/id:{project_id}/buildTypes"
        buildtypes = self._execute_teamcity_command(uri, method="GET")
        if "buildType" in buildtypes:
            return buildtypes["buildType"]
        return []

    def _get_vcs_roots_for_project(self, project_id):
        vcs_roots = []
        uri = f"/vcs-roots?locator=project:(id:{project_id})"
        vcs_roots_response = self._execute_teamcity_command(uri, method="GET")
        if "vcs-root" in vcs_roots_response:
            for vcs_root in vcs_roots_response["vcs-root"]:
                vcs_roots.append(vcs_root)
        return vcs_roots

    def _get_vcs_root_properties(self, vcs_root_id):
        uri = f"/vcs-roots/{vcs_root_id}/properties"
        properties = self._execute_teamcity_command(uri, method="GET")
        if "property" in properties:
            return properties["property"]
        return []

    def get_vcs_root_url(self, vcs_root_href):
        uri = f"{vcs_root_href}/properties/url"
        return self._execute_teamcity_command(uri, method="GET", is_text=True)

    def _update_vcs_root_properties(self, vcs_root_id, properties):
        uri = f"/vcs-roots/{vcs_root_id}/properties"
        return self._execute_teamcity_command(uri, method="PUT", data={"property": properties})

    def _get_buildtype_features(self, buildtype_id):
        uri = f"/buildTypes/id:{buildtype_id}/features"
        features = self._execute_teamcity_command(uri, method="GET")
        if "feature" in features:
            return features["feature"]
        return []

    def _update_buildtype_features(self, buildtype_id, features):
        uri = f"/buildTypes/id:{buildtype_id}/features"
        return self._execute_teamcity_command(uri, method="PUT", data={"feature": features})

    def generate_vcs_roots_csv(self, project_id, csv_file_path):
        try:
            vcs_roots = {}
            vcs_roots[project_id] = self._get_vcs_roots_for_project(project_id)
            subprojects = self._get_sub_projects(project_id)
            for subproject in subprojects:
                subproject_vcs_roots = self.generate_vcs_roots_csv(subproject["id"], "")
                vcs_roots.update(subproject_vcs_roots)
            if csv_file_path:
                with open(csv_file_path, mode="w", newline='') as csv_file:
                    fieldnames = ["project", "vcs_id", "vcs_href"]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for vcs_root_project, vcs_root_objects in vcs_roots.items():    
                        for vcs_root in vcs_root_objects:
                            writer.writerow({
                                "project": vcs_root_project,
                                "vcs_id": vcs_root["id"],
                                "vcs_href": vcs_root["href"]
                            })
                print(f"VCS roots list saved to '{csv_file_path}'")
            return vcs_roots
        except Exception as e:
            print(f"Error: {e}")

    def generate_buildtypes_csv(self, project_id, csv_file_path):
        try:
            buildTypes = {}
            buildTypes[project_id] = self._get_project_buildtypes(project_id)
            subprojects = self._get_sub_projects(project_id)
            for subproject in subprojects:
                subproject_buildtypes = self.generate_buildtypes_csv(subproject["id"], "")
                buildTypes.update(subproject_buildtypes)
            if csv_file_path:
                with open(csv_file_path, mode="w", newline='') as csv_file:
                    fieldnames = ["project", "buildtype_id", "buildtype_href"]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for buildtype_project, buildtype_objects in buildTypes.items():
                        for buildtype in buildtype_objects:
                            writer.writerow({
                                "project": buildtype_project,
                                "buildtype_id": buildtype["id"],
                                "buildtype_href": buildtype["href"]
                            })
                print(f"VCS roots list saved to '{csv_file_path}'")
            return buildTypes
        except Exception as e:
            print(f"Error: {e}")

    def update_vcs_url(self, vcs_href, new_git_url):
        try:
            vcs_root_id = vcs_href.removeprefix("/app/rest/vcs-roots/id:")
            properties = self._get_vcs_root_properties(vcs_root_id)
            if not properties:
                return
            updated_properties = []
            updated_properties_keys = []
            for original_property in properties:
                new_property = {
                    "name": original_property["name"],
                    "value": ""
                }
                if original_property["name"] == "url":
                    new_property["value"] = new_git_url
                elif original_property["name"] == "push_url":
                    new_property["value"] = new_git_url
                elif original_property["name"] == "authMethod":
                    new_property["value"] = "ACCESS_TOKEN"
                elif original_property["name"] == "oauthProviderId":
                    new_property["value"] = "PROJECT_EXT_138"
                elif original_property["name"] == "tokenType":
                    new_property["value"] = "refreshable"
                elif original_property["name"] == "username":
                    new_property["value"] = "oauth2"
                elif original_property["name"] == "usernameStyle":
                    new_property["value"] = "USERID"
                elif original_property["name"] == "secure:password":
                    continue
                else:
                    new_property["value"] = original_property["value"]
                updated_properties.append(new_property)
                updated_properties_keys.append(new_property["name"])
            if "authMethod" not in updated_properties_keys:
                updated_properties.append({
                    "name": "authMethod",
                    "value": "ACCESS_TOKEN"
                })
            elif "oauthProviderId" not in updated_properties_keys:
                updated_properties.append({
                    "name": "oauthProviderId",
                    "value": "PROJECT_EXT_138"
                })
            elif "tokenType" not in updated_properties_keys:
                updated_properties.append({
                    "name": "tokenType",
                    "value": "refreshable"
                })
            elif "username" not in updated_properties_keys:
                updated_properties.append({
                    "name": "username",
                    "value": "oauth2"
                })
            elif "usernameStyle" not in updated_properties_keys:
                updated_properties.append({
                    "name": "usernameStyle",
                    "value": "USERID"
                })
            self._update_vcs_root_properties(vcs_root_id, updated_properties)
        except Exception as e:
            print(f"Error: {e}")
            
    def update_buildtype_commit_status_publisher(self, buildtype_id):
        buildtype_features = self._get_buildtype_features(buildtype_id)
        updated_features = []
        for feature in buildtype_features:
            if feature["type"] != "commit-status-publisher":
                updated_features.append(feature)
                continue
            feature_properties = feature["properties"]["property"]
            publisher_vcs_root_id = ""
            should_update = False
            for property in feature_properties:
                if property["name"] == "stashBaseUrl" and self._bitbucket_server_host in property["value"]:
                    should_update = True
                if property["name"] == "vcsRootId":
                    publisher_vcs_root_id = property["value"]
            if should_update:
                updated_feature_properties = [
                    {
                        "name": "github_authentication_type",
                        "value": "vcsRoot"
                    },
                    {
                        "name": "github_host",
                        "value": "https://api.github.com"
                    },
                    {
                        "name": "publisherId",
                        "value": "githubStatusPublisher"
                    }
                ]
                
                if publisher_vcs_root_id:
                    updated_feature_properties.append({
                        "name": "vcsRootId",
                        "value": publisher_vcs_root_id
                    })
                feature["properties"]["property"] = updated_feature_properties
                updated_features.append(feature)
            else:
                updated_features.append(feature)
        self._update_buildtype_features(buildtype_id, updated_features)
