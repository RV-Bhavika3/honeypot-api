from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

API_KEY = "honeypot123"

# Home route
@app.route("/")
def home():
    return "Honeypot API running"

# Honeypot login
@app.route("/api/login", methods=["GET", "POST"])
def honeypot():
    ip = request.remote_addr
    time = datetime.now().isoformat()
    key = request.headers.get("X-API-KEY")

    print(f"[HONEYPOT] IP={ip}, TIME={time}, KEY={key}")

    if key != API_KEY:
        return jsonify({
            "status": "unauthorized",
            "message": "Invalid API key"
        }), 401

    return jsonify({
        "status": "success",
        "message": "Login attempt recorded"
    }), 200

# Hackathon /predict endpoint
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()  # get JSON input
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # ==============================
    # TODO: Add your hackathon logic here
    result = {
        "message": "Data received successfully",
        "your_data": data
    }
    # ==============================

    return jsonify(result), 200

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

