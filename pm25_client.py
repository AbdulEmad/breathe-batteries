import requests


class PM25Client:
    BASE_URL = "https://pm25.lass-net.org/API-1.0.0"

    def __init__(self, device_id):
        self.device_id = device_id

    def fetch_device_history(self):
        endpoint = f"/device/{self.device_id}/history/"
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
