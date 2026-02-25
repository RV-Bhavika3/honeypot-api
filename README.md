# Honeypot API Security Testing Tool

This project was developed during the HCL GUVI Hackathon.

## Project Overview
A honeypot-based API system designed to detect suspicious or malicious endpoint activity.  
The tool simulates vulnerable endpoints and logs incoming requests for analysis.

## Features
- Detects suspicious API requests
- Logs attacker behavior
- Simulates vulnerable endpoints
- API testing using Postman

## Tech Stack
Python  
Flask  
Postman

## How It Works
1. The server exposes honeypot endpoints.
2. Incoming requests are logged.
3. Suspicious patterns can be analyzed for security insights.

## Learning Outcomes
- Backend development using Flask
- API security concepts
- Logging and monitoring malicious requests

## How to Run the Project
1. Install dependencies
pip install -r requirements.txt

2. Run the Flask app
python app.py
