import os
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "HCL123"

@app.route("/")
def home():
    return "Honeypot API is running"

@app.route("/predict", methods=["POST"])
def predict():
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(force=True)
    ip = data.get("ip", "")
    endpoint = data.get("endpoint", "")
    payload = data.get("payload", "")

    suspicious = False
    if "admin" in endpoint.lower():
        suspicious = True
    if "drop" in payload.lower():
        suspicious = True
    if "select" in payload.lower():
        suspicious = True

    return jsonify({
        "ip": ip,
        "endpoint": endpoint,
        "suspicious": suspicious,
        "message": "Honeypot analysis complete"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render-assigned port
    app.run(host="0.0.0.0", port=port)
