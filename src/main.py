import os
import sys
import logging
import datetime
from sqlalchemy import text
from extract import search_tracks, get_artists, save_json
from transform import transform_data
from load import load_data, engine, get_last_successful_run_time

# 1. Setup Logging (Phase 10)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
logs_dir = os.path.join(base_dir, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(logs_dir, "etl.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("spotify_etl")

def insert_etl_metadata(start_time, end_time, extracted, loaded, status):
    """Inserts a run record into etl_metadata table."""
    try:
        stmt = text("""
            INSERT INTO etl_metadata (start_time, end_time, records_extracted, records_loaded, status)
            VALUES (:start_time, :end_time, :extracted, :loaded, :status)
        """)
        with engine.begin() as conn:
            conn.execute(stmt, {
                "start_time": start_time,
                "end_time": end_time,
                "extracted": extracted,
                "loaded": loaded,
                "status": status
            })
        logger.info("Successfully recorded run metadata in etl_metadata.")
    except Exception as e:
        logger.warning(f"Could not write run metadata to database: {e}. (This is normal if database is not running yet).")

def main():
    start_time = datetime.datetime.now()
    logger.info("========================================")
    logger.info("Starting Spotify ETL Pipeline execution.")
    logger.info("========================================")
    
    query = "ar rahman"
    status = "SUCCESS"
    records_extracted = 0
    records_loaded = 0
    
    try:
        # --- Check Incremental Metadata ---
        last_run_time = get_last_successful_run_time()
        logger.info(f"Last successful pipeline run time: {last_run_time}")
        
        # --- PHASE 2: Data Extraction ---
        logger.info(f"Step 1: Extracting tracks metadata for query '{query}' (limit: 50)...")
        tracks_data = search_tracks(query, 50)
        
        artist_ids = set()
        if "tracks" in tracks_data and "items" in tracks_data["tracks"]:
            items = tracks_data["tracks"]["items"]
            records_extracted = len(items)
            for track in items:
                for artist in track.get("artists", []):
                    if artist.get("id"):
                        artist_ids.add(artist["id"])
                        
        artist_ids = list(artist_ids)
        logger.info(f"Found {records_extracted} tracks. Fetching details for {len(artist_ids)} unique artists...")
        
        artists_data = get_artists(artist_ids)
        
        # Save raw files
        raw_dir = os.path.join(base_dir, "data", "raw")
        tracks_path = os.path.join(raw_dir, "tracks_raw.json")
        artists_path = os.path.join(raw_dir, "artists_raw.json")
        
        save_json(tracks_data, tracks_path)
        save_json(artists_data, artists_path)
        logger.info(f"Extraction completed. Raw files written to '{raw_dir}'.")
        
        # --- PHASES 3 & 4: Validation & Transformation ---
        logger.info("Step 2: Starting Validation and Transformation Layer...")
        validation_passed = transform_data(last_run_time)
        
        if not validation_passed:
            logger.warning("Data validation issues were found. Check logs/validation_report.txt for details.")
            
        # --- PHASES 5 & 6: Data Loading ---
        logger.info("Step 3: Loading processed data into PostgreSQL Data Warehouse...")
        records_loaded = load_data()
        
    except Exception as e:
        status = "FAILED"
        logger.error(f"ETL pipeline run failed: {e}", exc_info=True)
    finally:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Pipeline finished with status: {status} in {duration:.2f} seconds.")
        
        # Insert run metadata
        insert_etl_metadata(start_time, end_time, records_extracted, records_loaded, status)

if __name__ == "__main__":
    main()