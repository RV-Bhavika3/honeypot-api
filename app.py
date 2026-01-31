from flask import Flask, request, jsonify
import datetime
import re
import random
import os

app = Flask(__name__)

# 🔐 API Key (Render env OR fallback default)
MY_API_KEY = os.environ.get("MY_API_KEY", "HCL123")

# 🚦 Rate limit tracker
request_counts = {}
RATE_LIMIT = 20


# -------------------------
# Home Route (health check)
# -------------------------
@app.route('/', methods=["GET"])
def home():
    return jsonify({
        "message": "Honeypot API is running",
        "status": "ok"
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

    # Bank account numbers (6–16 digits)
    bank_pattern = r'\b\d{6,16}\b'
    bank_accounts = re.findall(bank_pattern, text)
    if bank_accounts:
        info["bank_accounts"] = bank_accounts

    # URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    if urls:
        info["urls"] = urls

    return info


# -------------------------
# 🤖 Agent Engagement Reply
# -------------------------
def fake_reply():
    replies = [
        "Verification in progress. Please resend your account details.",
        "Processing. Kindly confirm your UPI ID again.",
        "Security check running — share the payment link once more.",
        "Validation pending — please re-enter banking info."
    ]
    return random.choice(replies)


# -------------------------
# Main Endpoint — Honeypot
# -------------------------
@app.route('/predict', methods=['GET', 'POST'])
def predict():

    ip = request.remote_addr or "unknown"

    # 🚦 Rate limit trap
    if check_rate_limit(ip):
        return jsonify({
            "status": "blocked",
            "reason": "rate_limit"
        }), 429

    # 🔐 API Key check (supports both header styles)
    client_key = (
        request.headers.get("x-api-key")
        or request.headers.get("X-API-Key")
    )

    if client_key != MY_API_KEY:
        return jsonify({
            "status": "unauthorized",
            "message": "Invalid API key"
        }), 401

    # 📩 Accept input from JSON OR query OR empty
    data = request.get_json(silent=True) or {}
    user_input = data.get("example_input") or request.args.get("example_input") or ""

    # 🧠 Scam keyword detection
    keywords = [
        "bank","account","upi","otp","password","verify",
        "urgent","click","link","transfer","blocked",
        "admin","sql","hack","attack"
    ]

    is_scam = any(k in user_input.lower() for k in keywords)

    # 🔍 Extract intelligence
    extracted = extract_info(user_input)

    # 🪵 Log honeypot hit
    log_entry = {
        "time": str(datetime.datetime.now()),
        "ip": ip,
        "input": user_input,
        "scam": is_scam,
        "extracted": extracted
    }

    with open("honeypot_log.txt", "a") as f:
        f.write(str(log_entry) + "\n")

    # 🚨 Scam detected → engage
    if is_scam:
        return jsonify({
            "status": "scam_detected",
            "extracted_intelligence": extracted,
            "agent_reply": fake_reply()
        }), 200

    # ✅ Clean message
    return jsonify({
        "status": "clean",
        "message": "No scam pattern detected"
    }), 200


# -------------------------
# 🪤 Decoy Endpoint
# -------------------------
@app.route('/admin-login', methods=['GET','POST'])
def decoy():
    return jsonify({
        "status": "decoy",
        "note": "This endpoint is monitored"
    }), 200


# -------------------------
# Run (local only)
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
