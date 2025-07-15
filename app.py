import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# --------------------------------------------------------------------- #
#  ❖  INITIALISATION
# --------------------------------------------------------------------- #
load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# In-memory store – good enough for dev server
call_data: dict[str, str] = {}

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
        summary=call_data.get("summary"),
        vapi_public_key=VAPI_PUBLIC_KEY,
        assistant_id=ASSISTANT_ID,
    )

@app.route("/_update-summary", methods=["POST"])
def update_summary():
    data = request.get_json(silent=True) or {}
    print("[DEBUG] /_update-summary payload ▶", data)

    summary = data.get("summary")
    if summary:
        call_data["summary"] = summary
        print("[INFO] Summary stored.")
        return "", 200
    else:
        print("[WARN] 'summary' missing in request body!")
        return jsonify({"error": "summary_not_found"}), 400

@app.route("/_get-summary")
def get_summary():
    print("[DEBUG] GET /_get-summary called")
    summary = call_data.get("summary", "")
    print("[DEBUG] Returning JSON:", {"summary": summary})
    return jsonify({"summary": summary})

@app.route("/_fetch-call-summary/<call_id>")
def fetch_call_summary(call_id):
    """Securely fetch call summary from Vapi API."""
    try:
        url = f"https://api.vapi.ai/v1/calls/{call_id}"
        headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        summary = data.get("analysis", {}).get("summary", "")
        print("[DEBUG] Fetched summary from Vapi API:", summary)
        return jsonify({"summary": summary})
    except Exception as e:
        print("[ERROR] Failed to fetch from Vapi:", repr(e))
        return jsonify({"error": "fetch_failed"}), 500

# --------------------------------------------------------------------- #
#  ❖  ENTRY‑POINT
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
