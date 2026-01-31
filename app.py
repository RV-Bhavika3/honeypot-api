from flask import Flask, request, jsonify
import datetime
import re
import random
import os

app = Flask(__name__)

# 🔐 API Key (supports env var for Render, fallback default)
MY_API_KEY = os.environ.get("MY_API_KEY", "HCL123")

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
# 🔍 Intelligence Extraction
# -------------------------
def extract_info(text):
    info = {}

    # UPI IDs
    upi_pattern = r'\b[\w.-]+@[\w.-]+\b'
    upi_ids = re.findall(upi_pattern, text)
    if upi_ids:
        info["upi_ids"] = upi_ids

    # Bank account numbers (6–12 digits)
    bank_pattern = r'\b\d{6,12}\b'
    bank_accounts = re.findall(bank_pattern, text)
    if bank_accounts:
        info["bank_accounts"] = bank_accounts

    # URLs / phishing links
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    if urls:
        info["urls"] = urls

    return info


# -------------------------
# 🤖 Fake Engagement Replies
# -------------------------
def fake_reply():
    replies = [
        "Thank you — please share the full account details so I can verify.",
        "Processing request. Kindly resend your payment information.",
        "Verification pending. Please confirm your UPI ID again.",
        "I am checking — send the link once more to validate."
    ]
    return random.choice(replies)


# -------------------------
# Main Protected Endpoint
# -------------------------
@app.route('/predict', methods=['POST'])
def predict():

    ip = request.remote_addr or "unknown"

    # 🚦 Rate limit trap
    if check_rate_limit(ip):
        with open("honeypot_log.txt", "a") as f:
            f.write(f"RATE LIMIT TRIGGERED from {ip}\n")

        return jsonify({
            "status": "blocked",
            "reason": "rate_limit",
            "message": "Too many requests — flagged"
        }), 429

    # 🔐 API Key check
    client_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")

    if client_key != MY_API_KEY:
        return jsonify({
            "status": "unauthorized",
            "message": "Invalid or missing API key"
        }), 401

    # 📩 Get input safely
    data = request.get_json(silent=True) or {}
    user_input = data.get("example_input", "")

    # 🧠 Scam keyword detection
    suspicious_keywords = [
        "bank", "account", "upi", "otp", "password",
        "verify", "urgent", "click", "link",
        "hack", "attack", "drop", "sql", "admin"
    ]

    is_suspicious = any(word in user_input.lower() for word in suspicious_keywords)

    # 🔍 Extract intelligence
    extracted_info = extract_info(user_input)

    # 🪵 Log entry
    log_entry = {
        "time": str(datetime.datetime.now()),
        "endpoint": "/predict",
        "input": user_input,
        "suspicious": is_suspicious,
        "extracted": extracted_info,
        "ip": ip
    }

    with open("honeypot_log.txt", "a") as file:
        file.write(str(log_entry) + "\n")

    # 🚨 Suspicious → engage + extract
    if is_suspicious:
        return jsonify({
            "status": "scam_detected",
            "message": "Potential scam detected — engagement initiated",
            "extracted_intelligence": extracted_info,
            "agent_reply": fake_reply()
        }), 200

    # ✅ Safe message
    return jsonify({
        "status": "clean",
        "message": "No scam patterns detected"
    }), 200


# -------------------------
# 🪤 Decoy Endpoint
# -------------------------
@app.route('/admin-login', methods=['GET', 'POST'])
def fake_admin():

    ip = request.remote_addr or "unknown"

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
# Run Server (local only)
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
