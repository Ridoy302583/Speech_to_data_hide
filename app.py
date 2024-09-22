import os
import speech_recognition as sr
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import logging

app = Flask(__name__)
CORS(app)
recognizer = sr.Recognizer()

os.makedirs('uploads', exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

@app.route('/transcribe_text', methods=['POST'])
def transcribe_and_redact():
    try:
        if 'audio' not in request.files:
            logging.error("No audio file provided.")
            return jsonify({"error": "No audio file provided."}), 400

        file = request.files['audio']
        
        if file.filename == '':
            logging.error("No selected file.")
            return jsonify({"error": "No selected file."}), 400

        if not file.filename.endswith('.wav'):
            logging.error("Invalid file type. Only WAV files are allowed.")
            return jsonify({"error": "Invalid file type. Only WAV files are allowed."}), 400

        # Save the audio file temporarily
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        with sr.AudioFile(file_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.record(source)

        # Transcribe using Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio_data)
            logging.info(f"Transcription successful: {text}")

            # Redact personal information using the Groq LLM
            # client = Groq(api_key="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")
            # completion = client.chat.completions.create(
            #     model="llama-3.1-70b-versatile",
            #     messages=[
            #         {
            #             "role": "system",
            #             "content": """
            #             You are a Privacy Expert. Your task is to redact specific personal information from text data. Follow these guidelines:
            #             1. Hide any Name, Father's Name, and Mother's Name using `********`.
            #             2. If the text contains a mobile number, redact it by keeping the first three characters visible, followed by `*****`.
            #             3. Do not hide bank account numbers.
            #             4. Return the full modified text without revealing the redacted information.
            #             """
            #         },
            #         {
            #             "role": "user",
            #             "content": text,
            #         }
            #     ],
            #     temperature=1,
            #     max_tokens=1024,
            #     top_p=1,
            #     stream=False,
            #     stop=None,
            # )

            # # Extract and return the redacted result
            # result = completion.choices[0].message['content']
            # logging.info(f"Redacted text: {result}")
            return jsonify({"text": text}), 200

        except sr.UnknownValueError:
            logging.error("Google Speech Recognition could not understand the audio.")
            return jsonify({"error": "Google Speech Recognition could not understand the audio."}), 400
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service: {str(e)}")
            return jsonify({"error": f"Could not request results from Google Speech Recognition service: {str(e)}"}), 500

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
