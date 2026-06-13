# Spotify Music Analytics ETL Platform

## Project Overview
An end-to-end data engineering platform that continuously extracts music metadata from the Spotify Web API, validates and transforms the data, stores it in a PostgreSQL data warehouse, and exposes analytics through SQL queries and Power BI dashboards.

The system follows modern data engineering practices including modular ETL architecture, data validation, logging, testing, workflow orchestration using Airflow, Docker containerization, and incremental loading.

## Architecture Diagram
```text
Spotify API
    ↓
Authentication Layer (auth.py)
    ↓
Extraction Layer (extract.py) -> Raw JSON Storage (data/raw/)
    ↓
Validation Layer (validate.py)
    ↓
Transformation Layer (transform.py) -> Processed CSV Data (data/processed/)
    ↓
PostgreSQL Data Warehouse (load.py + schema.sql)
    ↓
SQL Analytics (analytics.sql)
    ↓
Airflow Orchestration (spotify_dag.py)
```

## Folder Structure
```text
spotify-etl-pipeline/
├── data/
│   ├── raw/                 # Raw JSON responses from API
│   └── processed/           # Transformed CSV files & validation reports
├── src/
│   ├── auth.py              # OAuth Access Token Management
│   ├── extract.py           # Track & Artist extraction logic
│   ├── validate.py          # Data quality checks & report generation
│   ├── transform.py         # Tabular data parser & feature engineering
│   ├── load.py              # SQLAlchemy DB Loader with Upserts
│   └── main.py              # Main pipeline orchestrator & logging
├── sql/
│   ├── schema.sql           # PostgreSQL Star Schema definition
│   └── analytics.sql        # Standard analytical queries
├── tests/
│   ├── conftest.py          # Pytest setup configuration
│   └── test_etl.py          # Pytest unit tests for ETL components
├── docker/
│   ├── Dockerfile           # Python application build
│   └── docker-compose.yml   # Multi-container service definitions
├── airflow/
│   └── dags/
│       └── spotify_dag.py   # Airflow Dag Orchestrator
└── logs/                    # Local file logs
```

## Environment Setup
Create a `.env` file in the root directory and add your Spotify API credentials:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

## How to Run

### Option 1: Docker Compose (Recommended)
Spins up PostgreSQL, Airflow Webserver, Airflow Scheduler, and builds the ETL container.
1. Run:
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
2. Access the Airflow UI at `http://localhost:8080` (default credentials: `admin` / `admin`).
3. You can access the PostgreSQL Database mapped to `localhost:5432` with user `postgres` / password `postgres` / database `spotify_db`.

### Option 2: Running Locally
1. Run local PostgreSQL database with credentials:
   - Database name: `spotify_db`
   - User/Password: `postgres`/`postgres`
2. Run the main ETL script:
   ```bash
   python src/main.py
   ```
3. Check the execution logs inside `logs/etl.log` and the validation report in `data/processed/validation_report.txt`.

## How to Test
Execute unit tests using pytest:
```bash
python -m pytest tests/test_etl.py
```

## Database Schema (Star Schema)

### Dimension Tables
* **`dim_artist`**: `artist_id` (PK), `artist_name`, `genres`, `followers`, `popularity`
* **`dim_album`**: `album_id` (PK), `album_name`, `release_date`, `release_year`, `release_month`, `release_decade`, `album_type`, `total_tracks`

### Fact Table
* **`fact_tracks`**: `track_id` (PK), `track_name`, `artist_id` (FK), `album_id` (FK), `duration_minutes`, `popularity`, `explicit`

### Metadata Table
* **`etl_metadata`**: `pipeline_run_id` (PK), `start_time`, `end_time`, `records_extracted`, `records_loaded`, `status`
