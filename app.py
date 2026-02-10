from flask import Flask, render_template, request
import os
import speech_recognition as sr
from textblob import TextBlob
from pydub import AudioSegment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import librosa
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

analyzer = SentimentIntensityAnalyzer()

def detect_voice_tone(filepath):
    try:
        y, sr_rate = librosa.load(filepath)
        energy = np.mean(librosa.feature.rms(y=y))

        if energy > 0.04:
            return "Positive"
        elif energy < 0.015:
            return "Negative"
        else:
            return "Neutral"
    except:
        return "Neutral"


@app.route("/", methods=["GET", "POST"])
def index():
    sentiment = None
    text = None
    voice_tone = None

    if request.method == "POST":
        try:
            file = request.files.get("audio")

            if not file or file.filename == "":
                return render_template("index.html", sentiment=None, text=None)

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # MP3 → WAV conversion
            if filepath.lower().endswith(".mp3"):
                sound = AudioSegment.from_mp3(filepath)
                wav_path = filepath.replace(".mp3", ".wav")
                sound.export(wav_path, format="wav")
                filepath = wav_path

            # ---------- VOICE TONE ANALYSIS ----------
            voice_tone = detect_voice_tone(filepath)

            # ---------- SPEECH TO TEXT ----------
            r = sr.Recognizer()
            try:
                with sr.AudioFile(filepath) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio)
            except:
                text = None

            # ---------- TEXT SENTIMENT ----------
            text_sentiment = "Neutral"
            if text:
                score = analyzer.polarity_scores(text)['compound']
                if score >= 0.05:
                    text_sentiment = "Positive"
                elif score <= -0.05:
                    text_sentiment = "Negative"

            # ---------- COMBINE BOTH ----------
            if voice_tone == "Positive" or text_sentiment == "Positive":
                sentiment = "Positive"
            elif voice_tone == "Negative" or text_sentiment == "Negative":
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        except:
            sentiment = "Neutral"
            text = None

    return render_template("index.html", sentiment=sentiment, text=text)


if __name__ == "__main__":
    app.run(debug=True)
