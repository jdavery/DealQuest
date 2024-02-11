from flask import jsonify
from prometheus_client import Counter
from . import app

# Define a counter for requests
REQUESTS = Counter('http_requests_total', 'Total HTTP Requests', ['endpoint'])

@app.route('/health')
def health():
    # Increment the request counter for the health endpoint
    REQUESTS.labels(endpoint='/health').inc()
    return '', 200

@app.route('/metrics')
def metrics():
    # Increment the request counter for the metrics endpoint
    REQUESTS.labels(endpoint='/metrics').inc()
    # Generate metrics data
    metrics_data = {'requests_per_second': 100}
    return jsonify(metrics_data), 200