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
        # Handle GET requests gracefully
        return jsonify({"message": "Send a POST request with JSON data"}), 200

    # Check API key
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Get JSON data
    data = request.get_json(force=True)
    message = data.get("message", {})
    conversation = data.get("conversationHistory", [])

    # Get latest scammer message
    text = message.get("text", "").lower()

    # Default reply
    reply = "Why is my account being suspended?"

    # Multi-turn logic based on latest message
    if conversation:  # if there is previous conversation
        if "upi" in text:
            reply = "Which UPI ID do you need me to provide?"
        elif "otp" in text:
            reply = "I did not receive any OTP yet."
        elif "bank" in text:
            reply = "Can you tell me which bank is affected?"
        elif "verify" in text:
            reply = "Can you clarify what I need to verify?"
        else:
            reply = "Could you clarify your request?"

    # Return structured JSON response
    return jsonify({
        "status": "success",
        "reply": reply
    })


if __name__ == "__main__":
    # Use Render-assigned port or fallback for local testing
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
