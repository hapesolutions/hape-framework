import requests
from src.configs.configurations import Configurations

class TeamsConnector:
    
    def __init__(self, webhook_url=None):
        self._webhook_url = webhook_url if webhook_url else Configurations.get_teams_webhook_url()
        if not self._webhook_url:
            raise ValueError("Missing TEAMS_WEBHOOK_URL in .env file or in the exported envionment variables.")
            
    def _send_message(self, color, title, message, details=None):
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color,
            "summary": title,
            "sections": [
                {
                    "activityTitle": title,
                    "activitySubtitle": message,
                    "activityImage": "",
                    "facts": [],
                }
            ],
        }
        
        if details:
            payload["sections"][0]["facts"].append({"name": "Details", "value": details})
            
        try:
            response = requests.post(self._webhook_url, json=payload)
            response.raise_for_status()
            print("Message sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")

    def send_success_message(self, message="Success", details=None):
        self._send_message("#00FF00", "Success", message, details)

    def send_failure_message(self, message="Failure", details=None):
        self._send_message("#FF0000", "Failure", message, details)
    
    def send_info_message(self, message="Information", details=None):
        self._send_message("#FFFF00", "Information", message, details)
