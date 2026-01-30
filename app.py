from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# 🔐 API Key
MY_API_KEY = "HCL123"

# 🚦 Simple in-memory rate tracker
request_counts = {}
RATE_LIMIT = 5


# -------------------------
# Home Route
# -------------------------
@app.route('/')
def home():
    return jsonify({
        "message": "Honeypot API is running"
    }), 200


# -------------------------
# Rate Limit Check
# -------------------------
def check_rate_limit(ip):
    count = request_counts.get(ip, 0) + 1
    request_counts[ip] = count
    return count > RATE_LIMIT


# -------------------------
# Main Protected Endpoint
# -------------------------
@app.route('/predict', methods=['POST'])
def predict():

    ip = request.remote_addr

    # 🚦 Rate limit trap
    if check_rate_limit(ip):
        with open("honeypot_log.txt", "a") as f:
            f.write(f"RATE LIMIT TRIGGERED from {ip}\n")

        return jsonify({
            "status": "blocked",
            "message": "Too many requests — flagged"
        }), 429

    # 🔐 API Key check
    client_key = request.headers.get("x-api-key")

    if client_key != MY_API_KEY:
        return jsonify({
            "status": "unauthorized",
            "message": "Invalid or missing API key"
        }), 401

    data = request.json
    user_input = data.get("example_input", "")

    suspicious_keywords = [
        "admin", "password", "root", "sql", "drop", "hack", "attack"
    ]

    is_suspicious = any(word in user_input.lower() for word in suspicious_keywords)

    log_entry = {
        "time": str(datetime.datetime.now()),
        "endpoint": "/predict",
        "input": user_input,
        "suspicious": is_suspicious,
        "ip": ip
    }

    with open("honeypot_log.txt", "a") as file:
        file.write(str(log_entry) + "\n")

    if is_suspicious:
        return jsonify({
            "status": "blocked",
            "message": "Suspicious activity detected and logged"
        }), 403

    return jsonify({
        "status": "allowed",
        "message": "Request processed safely"
    }), 200


# -------------------------
# 🪤 Decoy Endpoint
# -------------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def fake_admin():

    ip = request.remote_addr

    log_entry = {
        "time": str(datetime.datetime.now()),
        "endpoint": "/admin-login",
        "method": request.method,
        "ip": ip,
        "note": "Decoy endpoint triggered"
    }

    with open("honeypot_log.txt", "a") as file:
        file.write("DECOY HIT: " + str(log_entry) + "\n")

    return jsonify({
        "status": "decoy",
        "message": "This endpoint is monitored"
    }), 200


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
