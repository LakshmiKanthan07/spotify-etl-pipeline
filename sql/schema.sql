-- Star Schema for Spotify Music Analytics

-- 1. Dimension Tables
CREATE TABLE IF NOT EXISTS dim_artist (
    artist_id VARCHAR(50) PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    genres TEXT,
    followers INT,
    popularity INT
);

CREATE TABLE IF NOT EXISTS dim_album (
    album_id VARCHAR(50) PRIMARY KEY,
    album_name VARCHAR(255) NOT NULL,
    release_date VARCHAR(50),
    release_year INT,
    release_month INT,
    release_decade INT,
    album_type VARCHAR(50),
    total_tracks INT
);

-- 2. Fact Table
CREATE TABLE IF NOT EXISTS fact_tracks (
    track_id VARCHAR(50) PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    artist_id VARCHAR(50) REFERENCES dim_artist(artist_id) ON DELETE SET NULL,
    album_id VARCHAR(50) REFERENCES dim_album(album_id) ON DELETE SET NULL,
    duration_minutes NUMERIC(5, 2),
    popularity INT,
    explicit BOOLEAN
);

-- 3. ETL Metadata Table for pipeline monitoring
CREATE TABLE IF NOT EXISTS etl_metadata (
    pipeline_run_id SERIAL PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_extracted INT DEFAULT 0,
    records_loaded INT DEFAULT 0,
    status VARCHAR(50) NOT NULL
);
