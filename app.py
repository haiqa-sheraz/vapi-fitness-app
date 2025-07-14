import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# --------------------------------------------------------------------- #
#  ❖  INITIALISATION
# --------------------------------------------------------------------- #
load_dotenv()                                   # read .env

app = Flask(__name__)

# in‑memory store – good enough for a single‑process dev server
call_data: dict[str, str] = {}

# required environment variables
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID    = os.getenv("VAPI_ASSISTANT_ID")

if not VAPI_PUBLIC_KEY or not ASSISTANT_ID:     # fail fast
    raise RuntimeError(
        "[FATAL] VAPI_PUBLIC_KEY or VAPI_ASSISTANT_ID not set in environment"
    )

# --------------------------------------------------------------------- #
#  ❖  ROUTES
# --------------------------------------------------------------------- #
@app.route("/")
def index():
    """Serve front‑end, injecting last known summary (may be None)."""
    return render_template(
        "index.html",
        summary=call_data.get("summary"),       # may be None
        vapi_public_key=VAPI_PUBLIC_KEY,
        assistant_id=ASSISTANT_ID,
    )


@app.route("/_update-summary", methods=["POST"])
def update_summary():
    """Receive summary from front‑end and cache it in memory."""
    data = request.get_json(silent=True) or {}
    print("[DEBUG] /_update-summary payload ▶", data)   # ✨ extra logging

    summary = data.get("summary")
    if summary:
        call_data["summary"] = summary
        print("[INFO]  Summary stored.")
        return "", 200
    else:
        print("[WARN]  'summary' missing in request body!")
        return jsonify({"error": "summary_not_found"}), 400


@app.route("/_get-summary", methods=["GET"])
def get_summary():
    """Return the last cached summary (or empty string)."""
    return jsonify({"summary": call_data.get("summary", "")})


# --------------------------------------------------------------------- #
#  ❖  ENTRY‑POINT
# --------------------------------------------------------------------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO]  Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
