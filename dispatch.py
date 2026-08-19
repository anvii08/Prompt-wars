import os
from twilio.rest import Client

def send_emergency_alert(lat, lng, transcript_text):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    emergency_contacts = os.environ.get('EMERGENCY_CONTACT_NUMBERS', '')
    
    # Generate Google Maps link
    maps_link = "Location unavailable"
    if lat and lng:
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"

    # Compose the message
    message_body = (
        "URGENT: Guardian Call Emergency Alert\n\n"
        f"Location: {maps_link}\n\n"
        "Recent Transcript:\n"
        f"{transcript_text}"
    )

    # Check if we have Twilio credentials
    if not all([account_sid, auth_token, from_phone, emergency_contacts]):
        print("\n" + "="*50)
        print("[SIMULATED SMS ALERT]")
        print("="*50)
        print("To (Simulated):", emergency_contacts or "[No contacts specified]")
        print("Body:")
        print(message_body)
        print("="*50 + "\n")
        return True

    # Real dispatch
    try:
        client = Client(account_sid, auth_token)
        contacts = [c.strip() for c in emergency_contacts.split(',') if c.strip()]
        
        for contact in contacts:
            message = client.messages.create(
                body=message_body,
                from_=from_phone,
                to=contact
            )
            print(f"Sent emergency SMS to {contact}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send real SMS: {e}")
        # Even if it fails, don't crash the call
        return False

if __name__ == "__main__":
    send_emergency_alert("40.7128", "-74.0060", "User: Someone is following me\nAI: I'm here.")
