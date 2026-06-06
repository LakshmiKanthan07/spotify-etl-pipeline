# Spotify Music Analytics ETL Platform

## Project Overview
An end-to-end data engineering platform that continuously extracts music metadata from the Spotify Web API, validates and transforms the data, stores it in a PostgreSQL data warehouse, and exposes analytics through SQL queries and Power BI dashboards.

The system follows modern data engineering practices including modular ETL architecture, data validation, logging, testing, workflow orchestration using Airflow, Docker containerization, and incremental loading.

## Architecture Diagram
```text
Spotify API
    ↓
Authentication Layer
    ↓
Extraction Layer -> Raw JSON Storage (Data Lake)
    ↓
Validation Layer
    ↓
Transformation Layer -> Processed Data
    ↓
PostgreSQL Data Warehouse
    ↓
SQL Analytics
    ↓
Power BI Dashboard
```

## Installation Guide
1. Clone the repository.
2. Ensure you have Python installed.
3. Create a virtual environment and install the required dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Environment Setup
Create a `.env` file in the root directory and add your Spotify API credentials:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

## How to Run
Currently, the extraction layer is in progress. To test the Spotify API connection:
```bash
python src/test_spotify.py
python src/main.py
```
*(Full instructions will be added once Airflow and Docker are fully integrated)*

## Database Schema (Planned)

### Star Schema Design

**Dimension Tables:**
- `dim_artist`: `artist_id`, `artist_name`, `genres`, `followers`, `popularity`
- `dim_album`: `album_id`, `album_name`, `release_date`, `album_type`, `total_tracks`

**Fact Table:**
- `fact_tracks`: `track_id`, `track_name`, `artist_id`, `album_id`, `duration_minutes`, `popularity`, `explicit`

## Dashboard Screenshots
*(Screenshots of the Power BI dashboard will be added here once Phase 8 is completed)*

## Future Enhancements
- Implement Incremental Loading
- Add Data Quality Metrics
- Add CI/CD using GitHub Actions
- Add AWS Deployment (S3 -> Airflow -> RDS PostgreSQL -> Power BI)
