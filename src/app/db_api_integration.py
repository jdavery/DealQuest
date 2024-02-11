import sqlite3
import requests

DATABASE_FILE = 'games.db'
CHEAPSHARK_API_URL = 'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15'


def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS games (
                 internalName TEXT PRIMARY KEY,
                 title TEXT,
                 metacriticLink TEXT,
                 dealID TEXT,
                 storeID TEXT,
                 gameID TEXT,
                 salePrice REAL,
                 normalPrice REAL,
                 isOnSale INTEGER,
                 savings REAL,
                 metacriticScore INTEGER,
                 steamRatingText TEXT,
                 steamRatingPercent INTEGER,
                 steamRatingCount INTEGER,
                 steamAppID TEXT,
                 releaseDate INTEGER,
                 lastChange INTEGER,
                 dealRating REAL,
                 thumb TEXT)''')
    conn.commit()
    conn.close()


def fetch_deals_from_api():
    payload = {}
    headers = {}
    response = requests.request("GET", CHEAPSHARK_API_URL, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch deals from the API.")
        return []


def insert_data_from_api():
    data = fetch_deals_from_api()
    if isinstance(data, list):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        for entry in data:
            if isinstance(entry, dict):  # Ensure entry is a dictionary
                game_data = (
                    entry.get('internalName', ''),
                    entry.get('title', ''),
                    entry.get('metacriticLink', ''),
                    entry.get('dealID', ''),
                    entry.get('storeID', ''),
                    entry.get('gameID', ''),
                    float(entry.get('salePrice', 0)),
                    float(entry.get('normalPrice', 0)),
                    int(entry.get('isOnSale', 0)),
                    float(entry.get('savings', 0)),
                    int(entry.get('metacriticScore', 0)),
                    entry.get('steamRatingText', ''),
                    int(entry.get('steamRatingPercent', 0)),
                    int(entry.get('steamRatingCount', 0)),
                    entry.get('steamAppID', ''),
                    int(entry.get('releaseDate', 0)),
                    int(entry.get('lastChange', 0)),
                    float(entry.get('dealRating', 0)),
                    entry.get('thumb', '')
                )
                c.execute('''INSERT OR REPLACE INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', game_data)
            else:
                print("Invalid entry found in the data:", entry)
        conn.commit()
        conn.close()
    else:
        print("No valid data fetched from the API.")


def main():
    create_database()
    insert_data_from_api()
    print("Data inserted into the database successfully.")


if __name__ == "__main__":
    main()
