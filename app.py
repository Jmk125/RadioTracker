from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Define the path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'tracked_songs.db')

def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    query_artist = 'SELECT artist, COUNT(*) as count FROM songs GROUP BY artist'
    query_song = 'SELECT artist, song, COUNT(*) as count FROM songs GROUP BY artist, song'
    
    df_artist = pd.read_sql(query_artist, conn)
    df_song = pd.read_sql(query_song, conn)
    conn.close()
    
    return df_artist, df_song

def fetch_history(limit):
    conn = sqlite3.connect(DB_PATH)
    query_history = f'SELECT artist, song, timestamp FROM songs ORDER BY timestamp DESC LIMIT {limit}'
    df_history = pd.read_sql(query_history, conn)
    conn.close()
    return df_history

def fetch_top_artists(limit=20):
    conn = sqlite3.connect(DB_PATH)
    query_top_artists = f'''
        WITH ranked_artists AS (
            SELECT artist, COUNT(*) as count,
                   DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) as rank
            FROM songs
            GROUP BY artist
        )
        SELECT artist, count, rank
        FROM ranked_artists
        WHERE rank <= (
            SELECT MAX(rank)
            FROM (
                SELECT DISTINCT rank
                FROM ranked_artists
                ORDER BY rank
                LIMIT {limit}
            )
        )
        ORDER BY rank, artist
    '''
    df_top_artists = pd.read_sql(query_top_artists, conn)
    conn.close()
    return df_top_artists

def fetch_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch total number of plays
    cursor.execute('SELECT COUNT(*) FROM songs')
    total_plays = cursor.fetchone()[0]
    
    # Fetch total number of unique bands
    cursor.execute('SELECT COUNT(DISTINCT artist) FROM songs')
    total_bands = cursor.fetchone()[0]

    # Fetch total number of unique songs
    cursor.execute('SELECT COUNT(DISTINCT song || artist) FROM songs')
    total_unique_songs = cursor.fetchone()[0]
    
    # Fetch first and last timestamp
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM songs')
    first_timestamp, last_timestamp = cursor.fetchone()
    
    # Calculate total hours logged
    if first_timestamp and last_timestamp:
        first_time = datetime.strptime(first_timestamp, '%Y-%m-%d %H:%M:%S')
        last_time = datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S')
        total_seconds = (last_time - first_time).total_seconds()
        total_hours = total_seconds / 3600
    else:
        total_hours = 0
    
    conn.close()
    
    return {
        'total_plays': total_plays,
        'total_bands': total_bands,
        'total_unique_songs': total_unique_songs,
        'total_hours': round(total_hours, 2)
    }

@app.route('/api/data')
def data():
    df_artist, df_song = fetch_data()
    artist_data = df_artist.to_dict(orient='records')
    song_data = df_song.to_dict(orient='records')
    return jsonify({'artistData': artist_data, 'songData': song_data})

@app.route('/api/history')
def history():
    limit = request.args.get('limit', default=10, type=int)
    df_history = fetch_history(limit)
    history_data = df_history.to_dict(orient='records')
    return jsonify({'historyData': history_data})

@app.route('/api/top_artists')
def top_artists():
    df_top_artists = fetch_top_artists()
    top_artists_data = df_top_artists.to_dict(orient='records')
    return jsonify({'topArtistsData': top_artists_data})

@app.route('/api/summary')
def summary():
    summary_data = fetch_summary()
    return jsonify({'summaryData': summary_data})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
