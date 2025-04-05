from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import os

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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)