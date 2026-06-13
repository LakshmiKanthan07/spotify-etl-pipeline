import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# DB Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "spotify_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Setup database connection
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def init_db():
    """Reads schema.sql and creates tables if they do not exist."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    schema_path = os.path.join(base_dir, "sql", "schema.sql")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
    print("Database tables initialized successfully.")

def upsert_artists(df, conn):
    """Upserts artist records into dim_artist."""
    print(f"Upserting {len(df)} artists...")
    for _, row in df.iterrows():
        stmt = text("""
            INSERT INTO dim_artist (artist_id, artist_name, genres, followers, popularity)
            VALUES (:artist_id, :artist_name, :genres, :followers, :popularity)
            ON CONFLICT (artist_id) DO UPDATE SET
                artist_name = EXCLUDED.artist_name,
                genres = EXCLUDED.genres,
                followers = EXCLUDED.followers,
                popularity = EXCLUDED.popularity;
        """)
        conn.execute(stmt, {
            "artist_id": row["artist_id"],
            "artist_name": row["artist_name"],
            "genres": row["genres"],
            "followers": int(row["followers"]),
            "popularity": int(row["popularity"])
        })

def upsert_albums(df, conn):
    """Upserts album records into dim_album."""
    print(f"Upserting {len(df)} albums...")
    for _, row in df.iterrows():
        stmt = text("""
            INSERT INTO dim_album (album_id, album_name, release_date, release_year, release_month, release_decade, album_type, total_tracks)
            VALUES (:album_id, :album_name, :release_date, :release_year, :release_month, :release_decade, :album_type, :total_tracks)
            ON CONFLICT (album_id) DO UPDATE SET
                album_name = EXCLUDED.album_name,
                release_date = EXCLUDED.release_date,
                release_year = EXCLUDED.release_year,
                release_month = EXCLUDED.release_month,
                release_decade = EXCLUDED.release_decade,
                album_type = EXCLUDED.album_type,
                total_tracks = EXCLUDED.total_tracks;
        """)
        conn.execute(stmt, {
            "album_id": row["album_id"],
            "album_name": row["album_name"],
            "release_date": row["release_date"],
            "release_year": int(row["release_year"]),
            "release_month": int(row["release_month"]),
            "release_decade": int(row["release_decade"]),
            "album_type": row["album_type"],
            "total_tracks": int(row["total_tracks"])
        })

def upsert_tracks(df, conn):
    """Upserts track records into fact_tracks."""
    print(f"Upserting {len(df)} tracks...")
    for _, row in df.iterrows():
        stmt = text("""
            INSERT INTO fact_tracks (track_id, track_name, artist_id, album_id, duration_minutes, popularity, explicit)
            VALUES (:track_id, :track_name, :artist_id, :album_id, :duration_minutes, :popularity, :explicit)
            ON CONFLICT (track_id) DO UPDATE SET
                track_name = EXCLUDED.track_name,
                artist_id = EXCLUDED.artist_id,
                album_id = EXCLUDED.album_id,
                duration_minutes = EXCLUDED.duration_minutes,
                popularity = EXCLUDED.popularity,
                explicit = EXCLUDED.explicit;
        """)
        conn.execute(stmt, {
            "track_id": row["track_id"],
            "track_name": row["track_name"],
            "artist_id": row["artist_id"],
            "album_id": row["album_id"],
            "duration_minutes": float(row["duration_minutes"]),
            "popularity": int(row["popularity"]),
            "explicit": bool(row["explicit"])
        })

def load_data():
    """Main loading function that loads processed CSVs into database."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    processed_dir = os.path.join(base_dir, "data", "processed")
    
    artists_path = os.path.join(processed_dir, "artists.csv")
    albums_path = os.path.join(processed_dir, "albums.csv")
    tracks_path = os.path.join(processed_dir, "tracks.csv")
    
    if not os.path.exists(artists_path) or not os.path.exists(albums_path) or not os.path.exists(tracks_path):
        raise FileNotFoundError("Processed CSV files not found. Please run transformation first.")
        
    df_artists = pd.read_csv(artists_path)
    df_albums = pd.read_csv(albums_path)
    df_tracks = pd.read_csv(tracks_path)
    
    init_db()
    
    records_loaded = 0
    with engine.begin() as conn:
        upsert_artists(df_artists, conn)
        upsert_albums(df_albums, conn)
        upsert_tracks(df_tracks, conn)
        records_loaded = len(df_tracks)
        
    print(f"Data loading completed. Total tracks loaded/updated: {records_loaded}")
    return records_loaded

if __name__ == "__main__":
    load_data()
