import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# --------------------------------------------------------------------- #
#  ❖  INITIALIZATION
# --------------------------------------------------------------------- #
load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Environment variables
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
VAPI_API_KEY = os.getenv("VAPI_API_KEY")

if not VAPI_PUBLIC_KEY or not ASSISTANT_ID or not VAPI_API_KEY:
    raise RuntimeError("[FATAL] Missing one or more required environment variables")

# --------------------------------------------------------------------- #
#  ❖  ROUTES
# --------------------------------------------------------------------- #
@app.route("/")
def index():
    return render_template(
        "index.html",
        vapi_public_key=VAPI_PUBLIC_KEY,
        assistant_id=ASSISTANT_ID,
    )

@app.route("/_fetch-latest-summary")
def fetch_latest_summary():
    """Fetch summary of the most recent ended call from Vapi."""
    try:
        url = "https://api.vapi.ai/call?limit=5"
        headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
        response = requests.get(url, headers=headers)
        calls = response.json()

        if not isinstance(calls, list) or len(calls) == 0:
            print("[WARN] No call data received from Vapi.")
            return jsonify({"summary": ""})

        # Only consider calls that have ended
        ended_calls = [c for c in calls if c.get("status") == "ended"]
        if not ended_calls:
            print("[WARN] No ended calls found.")
            return jsonify({"summary": ""})

        # Sort by createdAt descending
        ended_calls.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        latest_call = ended_calls[0]

        # Get summary from either 'summary' or 'analysis.summary'
        summary = (
            latest_call.get("summary")
            or latest_call.get("analysis", {}).get("summary")
            or ""
        )

        print("[INFO] Latest Call ID:", latest_call.get("id"))
        print("[INFO] Summary Extracted:", summary)

        return jsonify({"summary": summary})

    except Exception as e:
        print("[ERROR] Failed to fetch latest summary:", repr(e))
        return jsonify({"summary": ""})

# --------------------------------------------------------------------- #
#  ❖  ENTRY‑POINT
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
