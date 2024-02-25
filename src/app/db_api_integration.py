import os
import requests
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
CHEAPSHARK_API_URL = 'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15'

def create_database():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    # Delete the existing 'games' table if it exists
    c.execute('DROP TABLE IF EXISTS games')
    # Create a new 'games' table
    c.execute('''CREATE TABLE games (
                 id SERIAL PRIMARY KEY,
                 title TEXT,
                 salePrice REAL,
                 normalPrice REAL,
                 savings REAL,
                 metacriticScore INTEGER,
                 steamRatingText TEXT,
                 steamRatingPercent INTEGER,
                 steamRatingCount INTEGER,
                 steamAppID TEXT,
                 dealRating REAL,
                 thumb TEXT)''')
    conn.commit()
    conn.close()

def fetch_deals_from_api():
    response = requests.get(CHEAPSHARK_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch deals from the API.")
        return []

def insert_data_from_api():
    data = fetch_deals_from_api()
    if isinstance(data, list):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        c = conn.cursor()
        for entry in data:
            if isinstance(entry, dict):
                game_data = (
                    entry.get('title', ''),
                    float(entry.get('salePrice', 0)),
                    float(entry.get('normalPrice', 0)),
                    float(entry.get('savings', 0)),
                    int(entry.get('metacriticScore', 0)),
                    entry.get('steamRatingText', ''),
                    int(entry.get('steamRatingPercent', 0)),
                    int(entry.get('steamRatingCount', 0)),
                    entry.get('steamAppID', ''),
                    float(entry.get('dealRating', 0)),
                    entry.get('thumb', '')
                )
                c.execute('''
                        INSERT INTO games 
                        (title, salePrice, normalPrice, savings, metacriticScore, steamRatingText, steamRatingPercent, steamRatingCount, steamAppID, dealRating, thumb)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', game_data)
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