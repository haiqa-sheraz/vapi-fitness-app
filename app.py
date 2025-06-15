## Folder structure:
# - app.py
# - templates/index.html
# - static/script.js
# - .env (for secrets)
# - requirements.txt

# 1. app.py

import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
call_data = {}

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://<your-ngrok>.ngrok.io/webhook

@app.route('/')
def index():
    return render_template('index.html', workout=call_data.get("workout"), vapi_public_key=VAPI_PUBLIC_KEY)

@app.route('/start-call', methods=['POST'])
def start_call():
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumber": None,
        "webhookUrl": WEBHOOK_URL
    }
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    res = requests.post("https://api.vapi.ai/calls", json=payload, headers=headers)
    return jsonify(res.json())

@app.route('/webhook', methods=['POST'])
def vapi_webhook():
    data = request.json
    print("Received webhook:", data)

    # We capture the assistant's last message that includes the workout
    if data['event'] == 'message':
        text = data.get('payload', {}).get('message', {}).get('content', '')
        if "Workout Plan:" in text:
            call_data['workout'] = text

    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
