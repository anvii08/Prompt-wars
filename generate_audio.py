import os
from gtts import gTTS

def generate_audio_clips():
    # Lines for the fake conversation
    lines = [
        "Hey, where are you right now?",
        "Okay, I'm waiting near the gate.",
        "Are you almost here?",
        "Take your time, no rush.",
        "Let me know when you're close."
    ]

    output_dir = os.path.join(os.path.dirname(__file__), "audio_clips")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Generating audio clips...")
    for i, line in enumerate(lines):
        filename = f"clip_{i+1}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        print(f"Generating {filename}: '{line}'")
        tts = gTTS(text=line, lang='en', slow=False)
        tts.save(filepath)
        
    print("Done generating audio clips.")

if __name__ == "__main__":
    generate_audio_clips()
