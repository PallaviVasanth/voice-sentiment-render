from flask import Flask, render_template, request
import os
import speech_recognition as sr
from textblob import TextBlob
from pydub import AudioSegment

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None
    text = None

    if request.method == "POST":
        try:
            file = request.files.get("audio")

            if file and file.filename != "":
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                # Convert MP3 to WAV if needed
                if filepath.lower().endswith(".mp3"):
                    sound = AudioSegment.from_mp3(filepath)
                    wav_path = filepath.replace(".mp3", ".wav")
                    sound.export(wav_path, format="wav")
                    filepath = wav_path

                r = sr.Recognizer()

                with sr.AudioFile(filepath) as source:
                    audio = r.record(source)

                try:
                    text = r.recognize_google(audio)
                except sr.UnknownValueError:
                    text = "Could not understand the audio clearly."
                except sr.RequestError:
                    text = "Speech recognition service unavailable."

                # Sentiment calculation (same logic as before)
                polarity = TextBlob(text).sentiment.polarity

                if polarity > 0:
                    sentiment = "Positive"
                elif polarity < 0:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"

        except Exception:
            text = "Error processing the audio file."
            sentiment = None

    return render_template("index.html", sentiment=sentiment, text=text)

if __name__ == "__main__":
    app.run()
