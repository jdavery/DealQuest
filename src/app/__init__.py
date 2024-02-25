import os
import psycopg2
from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re

DATABASE_URL = os.environ['DATABASE_URL']


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Function to fetch database fields from PostgreSQL database
def get_database_fields():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'games'
    """)
    columns = cursor.fetchall()

    # Extract column names from the result
    database_fields = [column[0] for column in columns]

    # Remove 'thumb' column if present
    database_fields = [field for field in database_fields if field != 'thumb']

    # Close the connection
    conn.close()
    return database_fields

# Define a route for the front page
@app.route("/", methods=["GET", "POST"])
def index():
    database_fields = get_database_fields()

    if request.method == "POST":
        if request.form.get("quick_search") == "very_positive":
            # Perform quick search for "Very Positive or Better"
            session['search_criteria'] = {"steamRatingText": ["Very Positive", "Overwhelmingly Positive"]}
            return redirect(url_for("results"))
        elif request.form.get("quick_search") == "under_10":
            # Perform quick search for "Under $10"
            session['search_criteria'] = {"salePrice": "< 10"}
            return redirect(url_for("results"))
        else:
            # Perform custom search
            session['search_criteria'] = {field: request.form.get(field) for field in database_fields if request.form.get(field)}
            return redirect(url_for("results"))

    return render_template("index.html", database_fields=database_fields)


# Define a route for the search results page
@app.route("/results")
def results():
    # Retrieve search criteria from session
    search_criteria = session.pop('search_criteria', None)

    # Perform the search operation based on the specified criteria
    results_df = perform_search(search_criteria)

    if results_df.empty:
        summary_stats = "No data available"
        correlation_matrix_plot = ""
    else:
        # Perform data analysis and computations
        # Compute summary statistics
        summary_stats = results_df.describe()
        df_numeric = results_df[['salePrice', 'normalPrice', 'metacriticScore', 'steamRatingPercent',
                                'steamRatingCount', 'dealRating']].copy()
        # Compute correlation matrix
        correlation_matrix = df_numeric.corr()

        # Plot correlation matrix as heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Matrix')

        # Save correlation matrix plot as base64 encoded image
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')  # Adjust bounding box to fit labels
        buffer.seek(0)
        correlation_matrix_plot = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

    # Render the search results page with the search criteria and results
    return render_template("results.html", search_criteria=search_criteria, results=results_df,
                           summary_stats=summary_stats, correlation_matrix_plot=correlation_matrix_plot)


# Function to perform the search operation
def perform_search(search_criteria):
    if not search_criteria:
        return pd.DataFrame()  # No criteria provided, return empty DataFrame

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    query = "SELECT * FROM games WHERE "
    conditions = []

    for field, value in search_criteria.items():
        if isinstance(value, list):
            conditions.append(f"{field} IN ({', '.join(['%s'] * len(value))})")
        elif isinstance(value, str) and any(op in value for op in ['<', '>', '=']):
            operator, numeric_value = re.findall(r'([<>=]+)\s*([\d.]+)', value)[0]  # Extract operator and numeric value
            conditions.append(f"{field} {operator} %s")
            search_criteria[field] = numeric_value.strip()  # Update value in search_criteria
        else:
            conditions.append(f"{field} = %s")
    query += " AND ".join(conditions)

    # Construct the list of values to be passed to the execute function
    values = [value if isinstance(value, list) else [value] for value in search_criteria.values()]
    flattened_values = [val for sublist in values for val in sublist]

    cursor.execute(query, flattened_values)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    # Create DataFrame from query results
    results_df = pd.DataFrame(rows, columns=columns)

    conn.close()

    print("Generated SQL Query:", query)
    print("Values:", flattened_values)

    return results_df

if __name__ == '__main__':
    app.run(debug=True)