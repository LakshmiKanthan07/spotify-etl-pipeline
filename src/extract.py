import requests
import os
import json
import time
import functools
import logging
from auth import get_access_token

logger = logging.getLogger("spotify_etl")

def retry_with_backoff(max_retries=5, initial_backoff=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            backoff = initial_backoff
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code if e.response is not None else 500
                    
                    if status_code == 429:
                        # Rate limited: Spotify returns Retry-After header in seconds
                        retry_after = 2.0
                        if e.response is not None and "Retry-After" in e.response.headers:
                            try:
                                retry_after = float(e.response.headers["Retry-After"])
                            except ValueError:
                                pass
                        logger.warning(f"Rate limited (429) on {func.__name__}. Sleeping {retry_after}s before retry {attempt}/{max_retries}...")
                        time.sleep(retry_after)
                    elif status_code >= 500:
                        logger.warning(f"Server error ({status_code}) on {func.__name__}. Sleeping {backoff}s before retry {attempt}/{max_retries}...")
                        time.sleep(backoff)
                        backoff *= 2
                    else:
                        raise e
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    logger.warning(f"Network error on {func.__name__}. Sleeping {backoff}s before retry {attempt}/{max_retries}...")
                    time.sleep(backoff)
                    backoff *= 2
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=5)
def _get_api_data(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def search_tracks(query="tamil", total_limit=50):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    page_size = 10
    items = []
    
    logger.info(f"Starting paginated track search for '{query}' (limit: {total_limit})")
    for offset in range(0, total_limit, page_size):
        params = {
            "q": query,
            "type": "track",
            "limit": min(page_size, total_limit - offset),
            "offset": offset
        }
        
        logger.info(f"Fetching search offset {offset}/{total_limit}...")
        page_data = _get_api_data("https://api.spotify.com/v1/search", headers, params)
        
        if "tracks" in page_data and "items" in page_data["tracks"]:
            page_items = page_data["tracks"]["items"]
            if not page_items:
                break
            items.extend(page_items)
        else:
            break
            
    return {
        "tracks": {
            "items": items
        }
    }

def get_artists(artist_ids):
    if not artist_ids:
        return {"artists": []}
    
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    artists = []
    for artist_id in artist_ids:
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        try:
            artist_data = _get_api_data(url, headers)
            artists.append(artist_data)
        except Exception as e:
            logger.error(f"Failed to fetch artist {artist_id}: {e}")
            raise e
        
    return {"artists": artists}

def save_json(data, filepath):
    dir_name = os.path.dirname(filepath)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
