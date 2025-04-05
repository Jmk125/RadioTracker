import os
import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# URL of the radio station's song history page
URL = 'https://www.audacy.com/stations/wncx/song-history'

# Configure options for headless mode
options = Options()
options.headless = True

# Specify the path to the Firefox binary
firefox_binary_path = 'C:/Program Files/Mozilla Firefox/firefox.exe'  # Update this path if needed
options.binary_location = firefox_binary_path

# Get the current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
geckodriver_path = os.path.join(current_dir, 'geckodriver.exe')

# Print the geckodriver path for debugging
print(f"Geckodriver path: {geckodriver_path}")

# Initialize the WebDriver (assuming geckodriver is in the same directory as this script)
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)

# Initialize SQLite database
conn = sqlite3.connect('tracked_songs.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song TEXT,
        artist TEXT,
        timestamp TEXT
    )
''')
conn.commit()

def get_now_playing():
    driver.get(URL)
    time.sleep(5)  # Wait for the page to load
    
    try:
        song_artist_info = driver.find_element(By.CLASS_NAME, 'css-1bcth50')
        song = song_artist_info.find_element(By.CLASS_NAME, 'title.css-1sho2pl').text.strip()
        artist = song_artist_info.find_element(By.CLASS_NAME, 'css-epvm6').text.strip()
        print(f"Retrieved song: {song}, artist: {artist}")
        return song, artist
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def track_songs(duration=3600, interval=60):
    end_time = time.time() + duration
    last_song = None
    last_artist = None

    while time.time() < end_time:
        song, artist = get_now_playing()
        if song and artist:
            if song != last_song or artist != last_artist:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO songs (song, artist, timestamp) VALUES (?, ?, ?)', (song, artist, timestamp))
                conn.commit()
                print(f"Logged song: {song}, artist: {artist} at {timestamp}")
                last_song = song
                last_artist = artist
            else:
                print(f"Song {song} by {artist} is still playing. No log entry created.")
        else:
            print("Could not retrieve song and artist information.")
        time.sleep(interval)
    
    print("Tracking complete. Data saved to tracked_songs.db")

if __name__ == "__main__":
    track_songs()
    driver.quit()
    conn.close()