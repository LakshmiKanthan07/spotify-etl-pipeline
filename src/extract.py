import requests
from auth import get_access_token

def search_tracks(query="tamil", limit=50):
    
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
    "https://api.spotify.com/v1/search",
    headers=headers,
    params={
        "q": query,
        "type": "track",
        "limit": limit
    }
)

    print(response.status_code)
    print(response.text)

    response.raise_for_status()

    return response.json()