import unittest
from unittest.mock import patch, MagicMock
from src.app.db_api_integration import fetch_deals_from_api

class TestDatabaseFunctions(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_deals_from_api(self, mock_get):
        # Mock the requests.get function and its response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'title': 'Game 1', 'salePrice': 10.0}, {'title': 'Game 2', 'salePrice': 20.0}]
        mock_get.return_value = mock_response

        # Call the function
        result = fetch_deals_from_api()

        # Check if requests.get was called with the correct URL
        mock_get.assert_called_once_with('https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15')
        # Check if the result is correct
        self.assertEqual(result, [{'title': 'Game 1', 'salePrice': 10.0}, {'title': 'Game 2', 'salePrice': 20.0}])

if __name__ == '__main__':
    unittest.main()