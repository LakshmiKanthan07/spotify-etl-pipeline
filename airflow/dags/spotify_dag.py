import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add the /opt/airflow/src directory to sys.path so we can import modules
sys.path.append("/opt/airflow/src")

from extract import search_tracks, get_artists, save_json
from transform import transform_data
from load import load_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_step():
    query = "ar rahman"
    tracks_data = search_tracks(query, 10)
    
    artist_ids = set()
    if "tracks" in tracks_data and "items" in tracks_data["tracks"]:
        for track in tracks_data["tracks"]["items"]:
            for artist in track.get("artists", []):
                if artist.get("id"):
                    artist_ids.add(artist["id"])
                    
    artists_data = get_artists(list(artist_ids))
    
    # Save to data directory inside container path
    # Raw directory setup
    base_dir = "/opt/airflow"
    raw_dir = os.path.join(base_dir, "data", "raw")
    
    save_json(tracks_data, os.path.join(raw_dir, "tracks_raw.json"))
    save_json(artists_data, os.path.join(raw_dir, "artists_raw.json"))

def transform_step():
    # Inside container we override the paths for source files
    # transform_data reads from data/raw and writes to data/processed
    # We set environment variable or rely on python file paths relative to project base /opt/airflow
    # Let's ensure directories match
    transform_data()

def load_step():
    load_data()

with DAG(
    'spotify_music_etl',
    default_args=default_args,
    description='Spotify music metadata ETL pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id='extract_raw_data',
        python_callable=extract_step,
    )

    transform_task = PythonOperator(
        task_id='validate_and_transform',
        python_callable=transform_step,
    )

    load_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_step,
    )

    extract_task >> transform_task >> load_task
