
import os
from groq import Groq

# Initialize Groq client
client = Groq(api_key="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")

# Define the correct path to the audio file in the uploads folder
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
filename = os.path.join(uploads_dir, "audio.wav")

# Open the audio file from the uploads directory
with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(filename, file.read()),
        model="whisper-large-v3",  # Using the specified model
        response_format="verbose_json"  # Return detailed transcription result
    )

# Print the transcription text
print(transcription.text)

      