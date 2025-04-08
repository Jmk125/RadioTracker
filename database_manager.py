import sqlite3
import os
from datetime import datetime

# Define the path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), 'tracked_songs.db')

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song TEXT,
            artist TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_entry():
    song = input("Enter the song name: ")
    artist = input("Enter the artist name: ")
    timestamp = input("Enter the timestamp (format: YYYY-MM-DD HH:MM:SS): ")
    if not timestamp:
        print("Timestamp is required. Please try again.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO songs (song, artist, timestamp) VALUES (?, ?, ?)', (song, artist, timestamp))
    conn.commit()
    conn.close()
    print(f"Added entry: {song} by {artist} at {timestamp}")

def delete_entry():
    print("\nHere are the current entries for reference:")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM songs ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(row)

    entry_ids = input("\nEnter the IDs of the entries to delete (comma-separated, e.g., 234, 235, 238): ")
    try:
        ids = [int(id.strip()) for id in entry_ids.split(',')]
    except ValueError:
        print("Invalid input. Please enter valid numeric IDs separated by commas.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany('DELETE FROM songs WHERE id = ?', [(id,) for id in ids])
    conn.commit()
    conn.close()
    print(f"\nDeleted entries with IDs: {', '.join(map(str, ids))}")

def update_entry():
    list_entries()
    entry_id = input("Enter the ID of the entry to update: ")
    song = input("Enter the new song name (leave blank to keep current): ")
    artist = input("Enter the new artist name (leave blank to keep current): ")
    timestamp = input("Enter the new timestamp (leave blank to keep current, format: YYYY-MM-DD HH:MM:SS): ")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if song:
        cursor.execute('UPDATE songs SET song = ? WHERE id = ?', (song, entry_id))
    if artist:
        cursor.execute('UPDATE songs SET artist = ? WHERE id = ?', (artist, entry_id))
    if timestamp:
        cursor.execute('UPDATE songs SET timestamp = ? WHERE id = ?', (timestamp, entry_id))
    conn.commit()
    conn.close()
    print(f"Updated entry with ID: {entry_id}")

def renumber_entries():
    """
    Renumber the entries in the database to remove gaps in the ID column.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all entries ordered by timestamp
    cursor.execute('SELECT id, song, artist, timestamp FROM songs ORDER BY timestamp ASC')
    rows = cursor.fetchall()

    # Create a temporary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song TEXT,
            artist TEXT,
            timestamp TEXT
        )
    ''')

    # Insert the sorted rows into the temporary table
    cursor.executemany('INSERT INTO temp_songs (song, artist, timestamp) VALUES (?, ?, ?)', 
                       [(song, artist, timestamp) for _, song, artist, timestamp in rows])

    # Drop the original table and rename the temporary table
    cursor.execute('DROP TABLE songs')
    cursor.execute('ALTER TABLE temp_songs RENAME TO songs')

    conn.commit()
    conn.close()
    print("\nDatabase renumbered successfully. IDs are now sequential.")

def list_entries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    limit_input = input("How many entries do you want to list? Enter a number or 'ALL': ").strip()

    if limit_input.upper() == 'ALL':
        cursor.execute('SELECT * FROM songs ORDER BY timestamp DESC')
    else:
        try:
            limit = int(limit_input)
            cursor.execute('SELECT * FROM songs ORDER BY timestamp DESC LIMIT ?', (limit,))
        except ValueError:
            print("Invalid input. Please enter a number or 'ALL'.")
            conn.close()
            return

    rows = cursor.fetchall()
    conn.close()

    print("\nEntries:")
    for row in rows:
        print(row)

def main():
    create_table()
    while True:
        list_entries()
        print("\nOptions: ")
        print("1. Add entry")
        print("2. Delete entry")
        print("3. Update entry")
        print("4. Renumber entries")
        print("5. Quit")
        
        choice = input("Enter your choice: ")
        if choice == '1':
            add_entry()
        elif choice == '2':
            delete_entry()
        elif choice == '3':
            update_entry()
        elif choice == '4':
            renumber_entries()
        elif choice == '5':
            print("Quitting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
