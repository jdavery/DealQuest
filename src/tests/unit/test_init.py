import unittest
import psycopg2
from unittest.mock import patch, MagicMock
from src.app.db_api_integration import create_database, fetch_deals_from_api

class TestDatabaseFunctions(unittest.TestCase):

    @patch('psycopg2.connect')
    @patch('psycopg2.Cursor')
    def test_create_database(self, mock_cursor, mock_connect):
        # Mock the psycopg2 connection and cursor
        mock_cursor_obj = MagicMock()
        mock_cursor.return_value = mock_cursor_obj
        mock_conn_obj = MagicMock()
        mock_connect.return_value = mock_conn_obj

        # Call the function
        create_database()

        # Check if execute was called with the correct SQL statements
        mock_cursor_obj.execute.assert_any_call('DROP TABLE IF EXISTS games')
        mock_cursor_obj.execute.assert_any_call('''CREATE TABLE games (
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
        # Check if commit was called
        mock_conn_obj.commit.assert_called_once()

    @patch('requests.get')
    def test_fetch_deals_from_api(self, mock_get):
        # Mock the requests.get function and its response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'title': 'Game 1', 'saleprice': 10.0}, {'title': 'Game 2', 'saleprice': 20.0}]
        mock_get.return_value = mock_response

        # Call the function
        result = fetch_deals_from_api()

        # Check if requests.get was called with the correct URL
        mock_get.assert_called_once_with('https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15')
        # Check if the result is correct
        self.assertEqual(result, [{'title': 'Game 1', 'saleprice': 10.0}, {'title': 'Game 2', 'saleprice': 20.0}])

if __name__ == '__main__':
    unittest.main()