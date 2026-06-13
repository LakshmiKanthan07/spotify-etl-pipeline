import json
import os
import pandas as pd
import numpy as np
from validate import check_nulls, check_duplicates, validate_ranges, generate_report

def extract_year_month(release_date):
    """Safely extracts year and month from Spotify's varied release_date formats."""
    if not isinstance(release_date, str) or not release_date:
        return 1900, 1
    
    parts = release_date.split("-")
    try:
        year = int(parts[0])
    except ValueError:
        year = 1900
        
    month = 1
    if len(parts) > 1:
        try:
            month = int(parts[1])
        except ValueError:
            month = 1
            
    return year, month

def transform_data(last_run_time=None):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    tracks_raw_path = os.path.join(raw_dir, "tracks_raw.json")
    artists_raw_path = os.path.join(raw_dir, "artists_raw.json")
    
    if not os.path.exists(tracks_raw_path) or not os.path.exists(artists_raw_path):
        raise FileNotFoundError("Raw data files not found. Please run extraction first.")
        
    # Read raw JSONs
    with open(tracks_raw_path, "r", encoding="utf-8") as f:
        tracks_raw = json.load(f)
    with open(artists_raw_path, "r", encoding="utf-8") as f:
        artists_raw = json.load(f)
        
    # 1. Transform Artists
    artists_list = []
    for artist in artists_raw.get("artists", []):
        if not artist:
            continue
        genres_str = ",".join(artist.get("genres", []))
        followers = artist.get("followers", {}).get("total", 0)
        artists_list.append({
            "artist_id": artist.get("id"),
            "artist_name": artist.get("name"),
            "genres": genres_str,
            "followers": followers,
            "popularity": artist.get("popularity", 0)
        })
    df_artists = pd.DataFrame(artists_list)
    
    # 2. Transform Albums & Tracks
    albums_dict = {}
    tracks_list = []
    
    for track in tracks_raw.get("tracks", {}).get("items", []):
        if not track:
            continue
            
        # Extract album
        album = track.get("album", {})
        if album and album.get("id"):
            album_id = album.get("id")
            if album_id not in albums_dict:
                release_date = album.get("release_date", "")
                year, month = extract_year_month(release_date)
                decade = (year // 10) * 10
                
                albums_dict[album_id] = {
                    "album_id": album_id,
                    "album_name": album.get("name"),
                    "release_date": release_date,
                    "release_year": year,
                    "release_month": month,
                    "release_decade": decade,
                    "album_type": album.get("album_type"),
                    "total_tracks": album.get("total_tracks", 0)
                }
                
        # Extract track attributes
        primary_artist_id = None
        artists_on_track = track.get("artists", [])
        if artists_on_track:
            primary_artist_id = artists_on_track[0].get("id")
            
        duration_ms = track.get("duration_ms", 0)
        duration_minutes = round(duration_ms / 60000.0, 2)
        
        popularity = track.get("popularity", 0)
        if popularity < 40:
            pop_cat = "Low"
        elif popularity < 70:
            pop_cat = "Medium"
        else:
            pop_cat = "High"
            
        tracks_list.append({
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "artist_id": primary_artist_id,
            "album_id": album.get("id"),
            "duration_minutes": duration_minutes,
            "popularity": popularity,
            "popularity_category": pop_cat,
            "explicit": bool(track.get("explicit", False))
        })
        
    df_albums = pd.DataFrame(list(albums_dict.values()))
    df_tracks = pd.DataFrame(tracks_list)
    
    # 3. Incremental Loading Filter
    if last_run_time is not None and not df_albums.empty:
        # Convert release_date to datetime for comparison
        df_albums['release_date_dt'] = pd.to_datetime(df_albums['release_date'], errors='coerce')
        cutoff = pd.Timestamp(last_run_time).normalize()
        
        # Keep only albums released since last successful run
        filtered_albums = df_albums[df_albums['release_date_dt'] >= cutoff]
        
        # If filtering results in empty dataset, we might want to log it
        print(f"Incremental Filter applied. Albums before: {len(df_albums)}, after: {len(filtered_albums)}")
        
        df_albums = filtered_albums.drop(columns=['release_date_dt'])
        
        # Filter tracks to only include those belonging to the remaining albums
        valid_album_ids = set(df_albums['album_id'])
        df_tracks = df_tracks[df_tracks['album_id'].isin(valid_album_ids)]
        
    # 4. Perform Validation (Phase 3)
    validation_checks = {}
    
    # Artists validation
    validation_checks["Artists Null IDs"] = check_nulls(df_artists, ["artist_id", "artist_name"])
    validation_checks["Artists Duplicates"] = check_duplicates(df_artists, "artist_id")
    validation_checks["Artists Popularity Range"] = validate_ranges(df_artists, "popularity", 0, 100)
    
    # Albums validation
    validation_checks["Albums Null IDs"] = check_nulls(df_albums, ["album_id", "album_name"]) if not df_albums.empty else (pd.DataFrame(), "")
    validation_checks["Albums Duplicates"] = check_duplicates(df_albums, "album_id") if not df_albums.empty else (pd.DataFrame(), "")
    validation_checks["Albums Track Count Range"] = validate_ranges(df_albums, "total_tracks", 0, 1000) if not df_albums.empty else (pd.DataFrame(), "")
    
    # Tracks validation
    validation_checks["Tracks Null IDs"] = check_nulls(df_tracks, ["track_id", "track_name", "artist_id", "album_id"]) if not df_tracks.empty else (pd.DataFrame(), "")
    validation_checks["Tracks Duplicates"] = check_duplicates(df_tracks, "track_id") if not df_tracks.empty else (pd.DataFrame(), "")
    validation_checks["Tracks Popularity Range"] = validate_ranges(df_tracks, "popularity", 0, 100) if not df_tracks.empty else (pd.DataFrame(), "")
    validation_checks["Tracks Duration Range"] = validate_ranges(df_tracks, "duration_minutes", 0, 180) if not df_tracks.empty else (pd.DataFrame(), "")
    
    # Write report
    report_path = os.path.join(processed_dir, "validation_report.txt")
    validation_passed = generate_report(validation_checks, report_path)
    print(f"Data Validation Completed. Status: {'PASSED' if validation_passed else 'FAILED'}. Report saved to: {report_path}")
    
    # 5. Save Processed Data
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        
    df_artists.to_csv(os.path.join(processed_dir, "artists.csv"), index=False, encoding="utf-8")
    df_albums.to_csv(os.path.join(processed_dir, "albums.csv"), index=False, encoding="utf-8")
    df_tracks.to_csv(os.path.join(processed_dir, "tracks.csv"), index=False, encoding="utf-8")
    
    print(f"Successfully saved transformed tables to: {processed_dir}")
    return validation_passed

if __name__ == "__main__":
    transform_data()
