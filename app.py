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
        if "audio" not in request.files:
            return render_template("index.html", sentiment=None, text=None)

        file = request.files["audio"]

        if file.filename == "":
            return render_template("index.html", sentiment=None, text=None)

        try:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Convert MP3 to WAV if needed
            if filepath.lower().endswith(".mp3"):
                try:
                    sound = AudioSegment.from_mp3(filepath)
                    wav_path = filepath.replace(".mp3", ".wav")
                    sound.export(wav_path, format="wav")
                    filepath = wav_path
                except:
                    sentiment = "Neutral"
                    text = None
                    return render_template("index.html", sentiment=sentiment, text=text)

            r = sr.Recognizer()

            with sr.AudioFile(filepath) as source:
                audio = r.record(source)

            try:
                text = r.recognize_google(audio)
            except:
                sentiment = "Neutral"
                text = None
                return render_template("index.html", sentiment=sentiment, text=text)

            # Sentiment logic
            polarity = TextBlob(text).sentiment.polarity

            if polarity > 0.1:
                sentiment = "Positive"
            elif polarity < -0.1:
                sentiment = "Negative"
            elif -0.1 <= polarity <= 0.1:
                sentiment = "Neutral"
            else:
                sentiment = "Neutral"

        except:
            sentiment = "Neutral"
            text = None

    return render_template("index.html", sentiment=sentiment, text=text)

if __name__ == "__main__":
    app.run()
