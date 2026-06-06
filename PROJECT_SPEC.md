# Project: Spotify Music Analytics ETL Platform

## Project Overview

Build a production-style end-to-end data engineering platform that continuously extracts music metadata from the Spotify Web API, validates and transforms the data, stores it in a PostgreSQL data warehouse, and exposes analytics through SQL queries and Power BI dashboards.

The system should follow modern data engineering practices including modular ETL architecture, data validation, logging, testing, workflow orchestration using Airflow, Docker containerization, and incremental loading.

The project should be designed such that the data source can be swapped in the future (Spotify API, Last.fm API, Deezer API, etc.) without changing the transformation or loading layers.

---

# Business Problem

Music streaming platforms generate massive amounts of data about artists, tracks, albums, genres, popularity, and listener engagement.

The goal is to build a centralized analytics platform that:

* Collects music metadata automatically
* Maintains a clean and queryable warehouse
* Supports analytical reporting
* Provides datasets for machine learning
* Demonstrates real-world ETL engineering practices

---

# Project Objectives

1. Extract artist, album, and track data from Spotify Web API.
2. Store raw API responses as JSON.
3. Validate incoming data quality.
4. Transform nested JSON into analytical tables.
5. Load processed data into PostgreSQL.
6. Build SQL analytics layer.
7. Build Power BI dashboards.
8. Schedule pipelines with Airflow.
9. Containerize services using Docker.
10. Add automated testing and logging.

---

# Final Architecture

Spotify API
↓
Authentication Layer
↓
Extraction Layer
↓
Raw JSON Storage
↓
Validation Layer
↓
Transformation Layer
↓
Processed Data Layer
↓
PostgreSQL Data Warehouse
↓
SQL Analytics
↓
Power BI Dashboard
↓
Machine Learning Ready Dataset

---

# Technology Stack

Programming Language:

* Python

Data Extraction:

* Requests
* Spotipy

Data Processing:

* Pandas
* NumPy

Database:

* PostgreSQL

ORM:

* SQLAlchemy

Workflow Orchestration:

* Apache Airflow

Containerization:

* Docker
* Docker Compose

Dashboard:

* Power BI

Testing:

* Pytest

Configuration:

* dotenv

Logging:

* Python logging module

Version Control:

* Git
* GitHub

---

# Folder Structure

spotify-etl-pipeline/

data/
├── raw/
├── processed/

src/
├── auth.py
├── extract.py
├── validate.py
├── transform.py
├── load.py
├── analytics.py
├── config.py
└── main.py

sql/
├── schema.sql
├── analytics.sql

tests/
├── test_auth.py
├── test_extract.py
├── test_transform.py
├── test_load.py

airflow/
├── dags/

docker/
├── Dockerfile
├── docker-compose.yml

logs/

dashboards/

.env
.gitignore
requirements.txt
README.md

---

# Phase 1: Authentication

Tasks:

* Load Spotify credentials from .env
* Generate access token
* Handle token expiration
* Centralize authentication logic

Deliverable:

auth.py

Functions:

get_access_token()

---

# Phase 2: Data Extraction

Tasks:

Extract:

Artists
Albums
Tracks

Data to collect:

Artist:

* artist_id
* artist_name
* genres
* popularity
* followers

Album:

* album_id
* album_name
* release_date
* album_type
* total_tracks

Track:

* track_id
* track_name
* popularity
* duration_ms
* explicit
* preview_url
* artist_id
* album_id

Store raw responses as JSON.

Output:

data/raw/

---

# Phase 3: Validation Layer

Checks:

1. Missing values
2. Duplicate records
3. Invalid popularity values
4. Invalid dates
5. Empty track names
6. Invalid IDs

Generate:

validation_report.txt

Deliverable:

validate.py

Functions:

check_nulls()
check_duplicates()
validate_ranges()
generate_report()

---

# Phase 4: Transformation Layer

Convert nested JSON to tabular format.

Create derived features:

duration_minutes
release_year
release_month
release_decade
popularity_category

Popularity Categories:

0-39 = Low
40-69 = Medium
70-100 = High

Output:

data/processed/

Deliverable:

transform.py

---

# Phase 5: Data Warehouse Design

Implement Star Schema.

Dimension Tables:

dim_artist
dim_album
dim_date

Fact Table:

fact_tracks

Relationships:

dim_artist
|
fact_tracks
|
dim_album

---

# PostgreSQL Schema

dim_artist

artist_id
artist_name
genres
followers
popularity

dim_album

album_id
album_name
release_date
album_type
total_tracks

fact_tracks

track_id
track_name
artist_id
album_id
duration_minutes
popularity
explicit

---

# Phase 6: Loading Layer

Tasks:

* Create tables automatically
* Insert new records
* Handle duplicate keys
* Implement incremental loading

Deliverable:

load.py

Functions:

load_artists()
load_albums()
load_tracks()

---

# Phase 7: Analytics Layer

Create SQL analytics queries.

Examples:

Top Artists

Most Popular Tracks

Average Popularity by Genre

Tracks Released Per Year

Explicit vs Non-Explicit Analysis

Albums by Decade

Artist Popularity Ranking

Store in:

sql/analytics.sql

---

# Phase 8: Dashboard

Power BI Dashboard Pages

Page 1: Executive Overview

KPIs:

* Total Artists
* Total Albums
* Total Tracks
* Average Popularity

Page 2: Artist Analysis

* Top Artists
* Artist Popularity
* Followers

Page 3: Album Analysis

* Albums by Year
* Albums by Type

Page 4: Genre Analysis

* Genre Distribution
* Genre Popularity

Page 5: Track Analysis

* Popularity Distribution
* Duration Distribution
* Explicit Content Analysis

---

# Phase 9: Airflow

Create DAG.

Workflow:

Extract
↓
Validate
↓
Transform
↓
Load
↓
Analytics

Schedule:

Daily

Requirements:

* Retry mechanism
* Logging
* Failure notifications

---

# Phase 10: Logging

Create logs for:

Authentication
Extraction
Transformation
Loading

Store logs in:

logs/

Example:

2026-06-06 12:00 Extract Started
2026-06-06 12:02 Extract Completed

---

# Phase 11: Testing

Implement Pytest.

Test Cases:

Authentication Tests

Extraction Tests

Transformation Tests

Loading Tests

Validation Tests

Coverage Target:

Minimum 80%

---

# Phase 12: Docker

Containerize:

PostgreSQL
Airflow
ETL Application

Create:

Dockerfile

docker-compose.yml

Single command startup:

docker compose up

---

# Phase 13: Documentation

README should include:

Project Overview

Architecture Diagram

Installation Guide

Environment Setup

How to Run

Database Schema

Dashboard Screenshots

Future Enhancements

---

# Phase 14: Advanced Features

Implement Incremental Loading

Maintain ETL Metadata Table

etl_metadata

Columns:

pipeline_run_id
start_time
end_time
records_extracted
records_loaded
status

Add Data Quality Metrics

Add CI/CD using GitHub Actions

Add AWS Deployment

Spotify API
↓
S3
↓
Airflow
↓
RDS PostgreSQL
↓
Power BI

---

# Expected Deliverables

* Working Spotify API Integration
* Raw JSON Data Lake
* Data Validation Framework
* Data Transformation Pipeline
* PostgreSQL Warehouse
* Star Schema Design
* SQL Analytics Layer
* Power BI Dashboard
* Airflow DAG
* Docker Deployment
* Unit Tests
* Logging Framework
* Complete Documentation

This project should resemble a production-grade data engineering and analytics platform rather than a simple API-to-database script.
