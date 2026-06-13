-- Analytics Layer Queries for Spotify Data Warehouse

-- 1. Top Artists by Follower Count
SELECT 
    artist_name, 
    followers, 
    popularity
FROM dim_artist
ORDER BY followers DESC
LIMIT 10;

-- 2. Most Popular Tracks
SELECT 
    t.track_name, 
    a.artist_name, 
    al.album_name, 
    t.popularity
FROM fact_tracks t
JOIN dim_artist a ON t.artist_id = a.artist_id
JOIN dim_album al ON t.album_id = al.album_id
ORDER BY t.popularity DESC
LIMIT 10;

-- 3. Average Popularity by Genre
-- Since genres are stored as a comma-separated string, we can split them using string functions (PostgreSQL specific: string_to_array and unnest)
WITH split_genres AS (
    SELECT 
        unnest(string_to_array(genres, ',')) AS genre,
        popularity
    FROM dim_artist
    WHERE genres IS NOT NULL AND genres <> ''
)
SELECT 
    genre,
    ROUND(AVG(popularity), 2) AS avg_popularity,
    COUNT(*) AS artist_count
FROM split_genres
GROUP BY genre
ORDER BY avg_popularity DESC, artist_count DESC;

-- 4. Tracks Released Per Year
SELECT 
    al.release_year, 
    COUNT(t.track_id) AS track_count
FROM fact_tracks t
JOIN dim_album al ON t.album_id = al.album_id
GROUP BY al.release_year
ORDER BY al.release_year DESC;

-- 5. Explicit vs Non-Explicit Track Analysis
SELECT 
    explicit, 
    COUNT(track_id) AS track_count,
    ROUND(AVG(popularity), 2) AS avg_popularity,
    ROUND(AVG(duration_minutes), 2) AS avg_duration_minutes
FROM fact_tracks
GROUP BY explicit;

-- 6. Albums Released by Decade
SELECT 
    release_decade, 
    COUNT(album_id) AS album_count
FROM dim_album
GROUP BY release_decade
ORDER BY release_decade DESC;

-- 7. Artist Popularity Ranking vs Follower Count Rank
SELECT 
    artist_name,
    popularity,
    RANK() OVER (ORDER BY popularity DESC) as popularity_rank,
    followers,
    RANK() OVER (ORDER BY followers DESC) as follower_rank
FROM dim_artist
ORDER BY popularity DESC;
