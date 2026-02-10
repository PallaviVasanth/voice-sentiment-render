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

            if not file or file.filename == "":
                return render_template("index.html", sentiment=None, text=None)

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # MP3 → WAV conversion
            if filepath.lower().endswith(".mp3"):
                try:
                    sound = AudioSegment.from_mp3(filepath)
                    wav_path = filepath.replace(".mp3", ".wav")
                    sound.export(wav_path, format="wav")
                    filepath = wav_path
                except:
                    # If conversion fails → treat as Neutral
                    return render_template("index.html", sentiment="Neutral", text=None)

            r = sr.Recognizer()

            try:
                with sr.AudioFile(filepath) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio)
            except:
                # If speech not detected → Neutral
                return render_template("index.html", sentiment="Neutral", text=None)

            # If text detected → sentiment analysis
            if text:
                polarity = TextBlob(text).sentiment.polarity

                if polarity > 0.1:
                    sentiment = "Positive"
                elif polarity < -0.1:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"
            else:
                sentiment = "Neutral"

        except:
            sentiment = "Neutral"
            text = None

    return render_template("index.html", sentiment=sentiment, text=text)

if __name__ == "__main__":
    app.run()
