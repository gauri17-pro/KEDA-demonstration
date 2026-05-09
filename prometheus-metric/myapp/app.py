from flask import Flask
from prometheus_client import Counter, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

# Prometheus Metric
REQUEST_COUNT = Counter(
    'hello_world_requests',
    'Total Hello World Requests'
)

@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return "Hello World from KEDA Demo!"

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        'Content-Type': CONTENT_TYPE_LATEST
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)