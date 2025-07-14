import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Store last call summary
call_data = {}

# Environment variables
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

@app.route('/')
def index():
    return render_template(
        'index.html',
        summary=call_data.get("summary"),
        vapi_public_key=VAPI_PUBLIC_KEY,
        ASSISTANT_ID=ASSISTANT_ID
    )

@app.route('/_update-summary', methods=['POST'])
def update_summary():
    data = request.get_json()
    summary = data.get("summary")
    if summary:
        call_data["summary"] = summary
        print("[INFO] Summary updated:", summary)
    else:
        print("[WARN] Summary not found in request.")
    return '', 200

@app.route('/_get-summary', methods=['GET'])
def get_summary():
    return jsonify({"summary": call_data.get("summary", "")})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
