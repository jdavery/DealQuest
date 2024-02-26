import os
import psycopg2
from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
from datetime import timedelta

DATABASE_URL = os.environ['DATABASE_URL']

app = Flask(__name__)
# Use heroku SECRET_KEY
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
# Set the permanent session lifetime to 10 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

# Function to fetch database fields from PostgreSQL database
def get_database_fields():
    conn = psycopg2.connect(DATABASE_URL)
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
    # Remove 'id' column if present
    database_fields = [field for field in database_fields if field != 'id']

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
            session['search_criteria'] = {"steamratingtext": ["Very Positive", "Overwhelmingly Positive"]}
            return redirect(url_for("results"))
        elif request.form.get("quick_search") == "under_10":
            # Perform quick search for "Under $10"
            session['search_criteria'] = {"saleprice": "< 10"}
            return redirect(url_for("results"))
        else:
            search_criteria = {field: request.form.get(field).strip() for field in database_fields if
                               request.form.get(field)}
            session['search_criteria'] = search_criteria
            return redirect(url_for("results"))
    else:
        # Check if there are stored search criteria and populate the form
        if 'search_criteria' in session:
            search_criteria = session['search_criteria']

        else:
            search_criteria = {}  # Empty dictionary if no search criteria in session

    return render_template("index.html", database_fields=database_fields, search_criteria=search_criteria)

# Define a route for the search results page
@app.route("/results")
def results():
    # Retrieve search criteria from session
    session_search_criteria = session.get('search_criteria', {})

    # Preprocess the session data to convert string representations of lists to actual lists
    search_criteria = {}
    for field, value in session_search_criteria.items():
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            try:
                # Attempt to evaluate the string as a list
                value = eval(value)
            except SyntaxError:
                pass  # Ignore if evaluation fails
        search_criteria[field] = value

    # Perform the search operation based on the specified criteria
    results_df = perform_search(search_criteria)

    if results_df.empty:
        summary_stats = "No games on sale match the search criteria."
        correlation_matrix_plot = ""
    else:
        # Perform data analysis and computations
        # Compute summary statistics
        summary_stats = results_df.describe()
        df_numeric = results_df[['saleprice', 'normalprice', 'metacriticscore', 'steamratingpercent',
                                'steamratingcount', 'dealrating']].copy()
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
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    if not search_criteria:
        cursor.execute("SELECT * FROM games")
    else:
        query = "SELECT * FROM games WHERE "
        conditions = []
        flattened_values = []

        for field, value in search_criteria.items():
            if isinstance(value, list):
                # Treat as a list
                print('its a list')
                conditions.append(f"{field} IN ({', '.join(['%s'] * len(value))})")
                flattened_values.extend(value)
            elif isinstance(value, str) and any(op in value for op in ['<', '>', '=']):
                # Handle numeric comparisons
                operator, numeric_value = re.findall(r'([<>=]+)\s*([\d.]+)', value)[0]
                conditions.append(f"{field} {operator} %s")
                flattened_values.append(numeric_value.strip())
            elif field in ['title', 'steamratingtext']:
                # Handle text comparisons
                conditions.append(f"{field} ILIKE %s")
                flattened_values.append(f"%{value}%")
            else:
                # Treat as single value
                conditions.append(f"{field} = %s")
                flattened_values.append(value)

        query += " AND ".join(conditions)

        cursor.execute(query, flattened_values)

    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    # Create DataFrame from query results
    results_df = pd.DataFrame(rows, columns=columns)

    conn.close()

    return results_df

if __name__ == '__main__':
    app.run(debug=True)