import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Store last structured workout
call_data = {}

# Environment variables
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # Add this to .env

LLAMA4_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-4-Scout-17B-16E-Instruct"

def get_structured_workout(transcript):
    prompt = f"""
    You are a fitness assistant. Your task is to extract and structure the workout routine from the following transcript.
    Respond in clear bullet points or numbered steps with formatting.

    Transcript:
    \"\"\"{transcript}\"\"\"

    Structured Workout Plan:
    """

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7
        }
    }

    response = requests.post(LLAMA4_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"].split("Structured Workout Plan:")[-1].strip()
    else:
        return "Sorry, could not generate workout plan."

@app.route('/')
def index():
    return render_template('index.html',
                           workout=call_data.get("workout"),
                           vapi_public_key=VAPI_PUBLIC_KEY,
                           ASSISTANT_ID=ASSISTANT_ID)

@app.route('/_update-workout', methods=['POST'])
def update_workout():
    data = request.get_json()
    transcript = data.get("workout")
    if transcript:
        structured_plan = get_structured_workout(transcript)
        call_data["workout"] = structured_plan
        return jsonify({"structured": structured_plan})
    return jsonify({"structured": ""})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
