from src.app.db_api_integration import create_database, fetch_deals_from_api
import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']


def test_create_database():
    # Test database creation
    create_database()

    # Connect to the database and verify that the table exists
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'games')")
    assert cursor.fetchone()[0] == True
    conn.close()


def test_fetch_deals_from_api():
    # Test fetching deals from API
    deals = fetch_deals_from_api()

    # Assert that deals are fetched and the response is not empty
    assert isinstance(deals, list)
    assert len(deals) > 0
