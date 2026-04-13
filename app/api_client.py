import requests

def get(url, headers):
    return requests.get(url, headers=headers)

def post(url, payload, headers):
    return requests.post(url, json=payload, headers=headers)

def patch(url, payload, headers):
    return requests.patch(url, json=payload, headers=headers)

def delete(url, headers):
    return requests.delete(url, headers=headers)