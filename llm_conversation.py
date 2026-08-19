import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# The instructions for the model
SYSTEM_INSTRUCTION = """
You are roleplaying as 'Dad'. The user is walking somewhere alone and feels unsafe. 
They are using this fake call to deter anyone nearby from bothering them. 
Keep the conversation casual, warm, and completely mundane — talk about dinner, 
what time they'll be back, asking them to grab something on the way, etc. 
Never say anything that reveals this is an AI or a safety app.

At the same time, silently monitor the user for signs of distress: 
explicit requests for help, fear, being followed, being grabbed, or 
any implication something is wrong. Also note if their responses seem 
panicked, cut off, or nonsensical.

You must always respond in this exact JSON format and nothing else:
{"reply": "<what you say out loud, natural conversational text>", "status": "normal" or "critical"}

Only ever set status to 'critical' if there is a real signal of distress 
in what the user said. Otherwise always 'normal'. The 'reply' text must 
NEVER acknowledge or reference the status — keep it sounding like an 
ordinary phone call at all times, even when status is critical.
"""

conversation_log = []

def reset_transcript():
    global conversation_log
    conversation_log = []

def get_recent_transcript(seconds=60):
    global conversation_log
    now = time.time()
    recent = [entry for entry in conversation_log if now - entry["time"] <= seconds]
    
    if not recent:
        return "[No recent transcript available]"
        
    lines = []
    for entry in recent:
        # Format as MM:SS relative to the start of the 60s window or just timestamp
        # A simple readable format:
        speaker = entry["speaker"]
        text = entry["text"]
        lines.append(f"{speaker}: {text}")
        
    return "\n".join(lines)

# Initialize model
try:
    # Use gemini-1.5-flash for fast responses
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={"response_mime_type": "application/json"}
    )
    chat_session = model.start_chat(history=[])
except Exception as e:
    print(f"Failed to initialize Gemini model: {e}")
    model = None
    chat_session = None

def get_ai_response(user_text):
    global conversation_log
    
    # Log user text
    conversation_log.append({"time": time.time(), "speaker": "User", "text": user_text})
    
    if not chat_session:
        # Fallback if API key missing or model fails to load
        reply, status = "I'm having trouble hearing you, are you there?", "normal"
        conversation_log.append({"time": time.time(), "speaker": "AI", "text": reply})
        return reply, status
        
    try:
        response = chat_session.send_message(user_text)
        
        # Parse JSON
        try:
            data = json.loads(response.text)
            reply = data.get("reply", "Yeah, okay.")
            status = data.get("status", "normal")
            # Enforce strict status string
            if status not in ["normal", "critical"]:
                status = "normal"
                
            conversation_log.append({"time": time.time(), "speaker": "AI", "text": reply})
            return reply, status
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM: {response.text}")
            reply, status = "Sorry, connection is bad, what did you say?", "normal"
            conversation_log.append({"time": time.time(), "speaker": "AI", "text": reply})
            return reply, status
            
    except Exception as e:
        print(f"Error getting AI response: {e}")
        reply, status = "Can you hear me?", "normal"
        conversation_log.append({"time": time.time(), "speaker": "AI", "text": reply})
        return reply, status

if __name__ == "__main__":
    # Standalone test
    print("Testing LLM Conversation (requires GEMINI_API_KEY in .env)")
    test_phrases = [
        "Hey dad, I'm just walking back from the library.",
        "It's a bit dark out here.",
        "Actually, someone is walking really close behind me.",
        "Help me!"
    ]
    
    for phrase in test_phrases:
        print(f"\nUser: {phrase}")
        reply, status = get_ai_response(phrase)
        print(f"Dad (Reply): {reply}")
        print(f"Internal Status: {status}")
