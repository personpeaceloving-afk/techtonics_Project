import requests

class APIClient:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def post(self, endpoint, payload):
        return requests.post(self.base_url + endpoint, json=payload, headers=self.headers)

    def get(self, endpoint):
        return requests.get(self.base_url + endpoint, headers=self.headers)

    def put(self, endpoint, payload):
        return requests.put(self.base_url + endpoint, json=payload, headers=self.headers)

    def patch(self, endpoint, payload):
        return requests.patch(self.base_url + endpoint, json=payload, headers=self.headers)

    def delete(self, endpoint):
        return requests.delete(self.base_url + endpoint, headers=self.headers)