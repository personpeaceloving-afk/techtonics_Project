from app.api_client import get

def get_categories():
    data = get("part/category/")
    return [c["name"] for c in data]