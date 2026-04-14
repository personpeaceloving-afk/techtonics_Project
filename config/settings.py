import os

BASE_URL = os.getenv("BASE_URL", "https://demo.inventree.org/api")
CATEGORY_ENDPOINT = "/part/category/"
AUTH_TOKEN = os.getenv("INVENTREE_TOKEN", "inv-61024d3ac9cd26e883afdc67848baaa137a46512-20260414")