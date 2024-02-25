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
                 saleprice REAL,
                 normalprice REAL,
                 savings REAL,
                 metacriticscore INTEGER,
                 steamratingtext TEXT,
                 steamratingpercent INTEGER,
                 steamratingcount INTEGER,
                 steamappid TEXT,
                 dealrating REAL,
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
                    float(entry.get('saleprice', 0)),
                    float(entry.get('normalprice', 0)),
                    float(entry.get('savings', 0)),
                    int(entry.get('metacriticscore', 0)),
                    entry.get('steamratingtext', ''),
                    int(entry.get('steamratingpercent', 0)),
                    int(entry.get('steamratingcount', 0)),
                    entry.get('steamappid', ''),
                    float(entry.get('dealrating', 0)),
                    entry.get('thumb', '')
                )
                c.execute('''
                        INSERT INTO games 
                        (title, saleprice, normalprice, savings, metacriticscore, steamratingtext, steamratingpercent, 
                        steamratingcount, steamappid, dealrating, thumb)
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