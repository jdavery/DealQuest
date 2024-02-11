import sqlite3
import pandas as pd


# Function to connect to the SQLite database
def connect_to_database(database_file):
    conn = sqlite3.connect(database_file)
    return conn


# Function to perform a SQL query and fetch results
def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# Main function to execute the script
def main():
    # Connect to the SQLite database
    conn = connect_to_database('games.db')

    # Retrieve relevant columns from the database table
    query = ("SELECT salePrice, normalPrice, metacriticScore, steamRatingPercent, steamRatingCount, dealRating "
             "FROM games")
    data = pd.read_sql_query(query, conn)

    # Calculate correlation coefficients
    correlation_matrix = data.corr()

    # Print correlation matrix
    print("Correlation Matrix:")
    print(correlation_matrix)

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()
