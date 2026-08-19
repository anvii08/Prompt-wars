# Guardian Call

A safety app designed for when you're walking alone. It fakes an active phone call to deter harassment, while silently monitoring your live microphone using a Gemini-powered AI. If the AI detects distress or a safe word, it automatically dispatches an emergency SMS with your live GPS location and a transcript to your contacts.

## Deployment

To deploy this application to a production hosting platform (like Render or Railway), follow these instructions:

1. **HTTPS is Required**: Modern browsers require an active HTTPS connection to request Microphone and Geolocation permissions. When you deploy to platforms like Render, they automatically provision a secure HTTPS URL for you. The app will not work over plain HTTP in production.
2. **Environment Variables**: You must set the following environment variables in your hosting provider's dashboard:
   - `GEMINI_API_KEY`: Your Google AI Studio API key for the conversational AI.
   - `TWILIO_ACCOUNT_SID`: (Optional) Your Twilio Account SID.
   - `TWILIO_AUTH_TOKEN`: (Optional) Your Twilio Auth Token.
   - `TWILIO_PHONE_NUMBER`: (Optional) Your Twilio sending phone number.
   - `EMERGENCY_CONTACT_NUMBERS`: (Optional) Comma-separated list of phone numbers to alert (e.g., `+1234567890,+0987654321`).
   
   *Note: If you leave the Twilio variables blank, the app will safely fall back to printing a "Simulated SMS Alert" in your server logs instead of crashing.*

3. **Start Command**: Configure your deployment to use `gunicorn` to run the Flask app from within the `backend` directory. The `Procfile` is already configured for this:
   ```bash
   gunicorn app:app --chdir backend
   ```
