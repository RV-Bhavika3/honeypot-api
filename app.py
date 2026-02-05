import os
import re
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---------------------
# Configuration
# ---------------------
API_KEY = "HCL123"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# In-memory storage for conversation intelligence
sessions_intelligence = {}

# Scam detection keywords
SCAM_KEYWORDS = ["account", "upi", "verify", "blocked", "password", "bank"]

# ---------------------
# Routes
# ---------------------
@app.route("/")
def home():
    return "Honeypot API is running"

@app.route("/predict", methods=["GET", "POST"])
def predict():
    # Handle GET requests gracefully
    if request.method == "GET":
        return jsonify({"message": "Send a POST request with JSON data"}), 200

    # ---------------------
    # API Key Validation
    # ---------------------
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"status": "error", "reply": "Unauthorized"}), 401

    # ---------------------
    # Parse Request JSON
    # ---------------------
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "reply": "Invalid JSON"}), 400

    session_id = data.get("sessionId")
    message_text = data.get("message", {}).get("text", "")
    conversation_history = data.get("conversationHistory", [])

    if not session_id or not message_text:
        return jsonify({"status": "error", "reply": "Missing sessionId or message"}), 400

    # ---------------------
    # Scam Detection
    # ---------------------
    scam_detected = any(word.lower() in message_text.lower() for word in SCAM_KEYWORDS)

    # ---------------------
    # Intelligence Extraction
    # ---------------------
    intelligence = sessions_intelligence.get(session_id, {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    })

    # Extract UPI IDs
    upi_matches = re.findall(r"\b[\w.-]+@upi\b", message_text)
    intelligence["upiIds"].extend([uid for uid in upi_matches if uid not in intelligence["upiIds"]])

    # Extract phone numbers
    phone_matches = re.findall(r"\+?\d{10,12}", message_text)
    intelligence["phoneNumbers"].extend([p for p in phone_matches if p not in intelligence["phoneNumbers"]])

    # Extract phishing links
    link_matches = re.findall(r"http[s]?://\S+", message_text)
    intelligence["phishingLinks"].extend([l for l in link_matches if l not in intelligence["phishingLinks"]])

    # Extract suspicious keywords
    for kw in SCAM_KEYWORDS:
        if kw.lower() in message_text.lower() and kw not in intelligence["suspiciousKeywords"]:
            intelligence["suspiciousKeywords"].append(kw)

    # Save intelligence for this session
    sessions_intelligence[session_id] = intelligence

    # ---------------------
    # Generate Decoy Reply
    # ---------------------
    if "account" in message_text.lower():
        reply_text = "Why is my account being suspended?"
    elif "upi" in message_text.lower() or "bank" in message_text.lower():
        reply_text = "Can you explain the issue in detail?"
    else:
        reply_text = "Thank you for your message."

    # ---------------------
    # Optional: Send Final Callback to GUVI
    # Trigger if conversation has more than 3 messages or scam detected
    # ---------------------
    if scam_detected and len(conversation_history) >= 3:
        final_payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(conversation_history) + 1,
            "extractedIntelligence": intelligence,
            "agentNotes": "Conversation handled by AI honeypot. Scammer used urgency/payment keywords."
        }
        try:
            requests.post(
                GUVI_CALLBACK_URL,
                json=final_payload,
                timeout=5
            )
        except Exception as e:
            print("Callback failed:", e)

    # ---------------------
    # Return Response
    # ---------------------
    return jsonify({
        "status": "success",
        "reply": reply_text
    })


# ---------------------
# Run App
# ---------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
