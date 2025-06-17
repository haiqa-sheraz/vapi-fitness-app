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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

LLAMA4_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-4-Scout-17B-16E-Instruct"

def structure_workout(transcript):
    prompt = f"""
You are a fitness assistant. Extract and structure the workout plan from this transcript.
Respond in clean bullet points or numbers, suitable for display.

Transcript:
\"\"\"{transcript}\"\"\"

Workout Plan:
"""
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 300
        }
    }

    try:
        response = requests.post(LLAMA4_API_URL, headers=headers, json=payload)
        print("Response from Llama4:", response.status_code, response.text)

        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list) and "generated_text" in result[0]:
                text = result[0]["generated_text"]
            elif isinstance(result, dict) and "generated_text" in result:
                text = result["generated_text"]
            else:
                return "Could not extract workout from response."

            structured = text.split("Workout Plan:")[-1].strip()
            return structured if structured else "Workout plan not found in response."
        else:
            return "Error: Llama4 API did not return 200."
    except Exception as e:
        return f"Error processing workout plan: {str(e)}"

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
        structured = structure_workout(transcript)
        call_data["workout"] = structured
        return jsonify({"structured": structured})
    return jsonify({"structured": ""})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
