import requests

# ==========================================
# HELPER: FETCH RAW JSON FROM GITHUB
# ==========================================
def fetch_github_json(url: str, name: str):
    try:
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            raise Exception(f"{name} URL returned {response.status_code}")

        try:
            return response.json()
        except ValueError:
            raise Exception(f"{name} URL does not contain valid JSON")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching {name}: {str(e)}")

