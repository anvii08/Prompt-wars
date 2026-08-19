import os
import time
import threading
import io
from gtts import gTTS
from flask import Flask, jsonify, render_template, request, send_file
from llm_conversation import get_ai_response, get_recent_transcript, reset_transcript
from dispatch import send_emergency_alert

app = Flask(__name__)

call_status = "normal"
is_call_active = False
alert_already_sent = False
user_lat = None
user_lng = None

def trigger_critical():
    global call_status, alert_already_sent, user_lat, user_lng
    call_status = "critical"
    
    if not alert_already_sent:
        alert_already_sent = True
        print("CRITICAL STATUS REACHED. Dispatching emergency alert...")
        transcript = get_recent_transcript(60)
        
        threading.Thread(
            target=send_emergency_alert, 
            args=(user_lat, user_lng, transcript),
            daemon=True
        ).start()

def generate_audio_response(text):
    if not text:
        return None
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        print(f"Error in TTS: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_location', methods=['POST'])
def update_location():
    global user_lat, user_lng
    data = request.json
    if data:
        user_lat = data.get('lat')
        user_lng = data.get('lng')
    return jsonify({"status": "success"})

@app.route('/start_call', methods=['POST'])
def start_call():
    global is_call_active, call_status, alert_already_sent
    is_call_active = True
    call_status = "normal"
    alert_already_sent = False
    reset_transcript()
    return jsonify({"status": "started"})

@app.route('/end_call', methods=['POST'])
def end_call():
    global is_call_active
    is_call_active = False
    return jsonify({"status": "ended"})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"call_status": call_status})

@app.route('/trigger_critical', methods=['POST'])
def api_trigger_critical():
    trigger_critical()
    return jsonify({"status": "critical_triggered"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
        
    text = data['text']
    print(f"Heard from frontend: {text}")
    
    reply, status = get_ai_response(text)
    
    if status == "critical":
        trigger_critical()
        
    print(f"AI replied: {reply}")
    
    mp3_fp = generate_audio_response(reply)
    if mp3_fp:
        return send_file(mp3_fp, mimetype="audio/mpeg")
    else:
        return jsonify({"error": "Failed to generate audio"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
