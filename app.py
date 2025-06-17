import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Store last workout message
call_data = {}

# Environment variables
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

@app.route('/')
def index():
    return render_template('index.html',
                           workout=call_data.get("workout"),
                           vapi_public_key=VAPI_PUBLIC_KEY,
                           ASSISTANT_ID=ASSISTANT_ID)

@app.route('/_update-workout', methods=['POST'])
def update_workout():
    data = request.get_json()
    workout = data.get("workout")
    if workout:
        call_data["workout"] = workout
    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)