import requests
import os
import json
from auth import get_access_token

def search_tracks(query="tamil", limit=10):
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

    response.raise_for_status()
    return response.json()

def get_artists(artist_ids):
    if not artist_ids:
        return {"artists": []}
    
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    artists = []
    for artist_id in artist_ids:
        response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_id}",
            headers=headers
        )
        response.raise_for_status()
        artists.append(response.json())
        
    return {"artists": artists}

def save_json(data, filepath):
    # Ensure directory exists
    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)