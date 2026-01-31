import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# API key required for authentication
API_KEY = "HCL123"

@app.route("/")
def home():
    return "Honeypot API is running"

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        # Handle GET requests gracefully to avoid 405
        return jsonify({"message": "Send a POST request with JSON data"}), 200

    # POST request processing
    key = request.headers.get("x-api-key")
    
    # Require correct API key
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Get JSON data
    data = request.get_json(force=True)
    ip = data.get("ip", "")
    endpoint = data.get("endpoint", "")
    payload = data.get("payload", "")

    # Honeypot detection logic
    suspicious = False
    if "admin" in endpoint.lower():
        suspicious = True
    if "drop" in payload.lower():
        suspicious = True
    if "select" in payload.lower():
        suspicious = True

    # Return response
    return jsonify({
        "ip": ip,
        "endpoint": endpoint,
        "suspicious": suspicious,
        "message": "Honeypot analysis complete"
    })


if __name__ == "__main__":
    # Use Render-assigned port or fallback for local testing
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
