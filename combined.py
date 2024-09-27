import requests
import json
import os
import re
from flask import Flask, request, render_template
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip
from moviepy.config import change_settings
from gtts import gTTS

# Secret API key (replace with the actual key)
from Secret_Key import api_key

# Load the API key from environment variable
Api_Key = os.getenv('api_key')

app = Flask(__name__)

# Part 1: Text Generation Code
def get_answer(question):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": question}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s.,!?;:]', '', text)
    return text

# Part 2: Video Generation Code
# Path to the ImageMagick executable
imagemagick_path = r"C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"
change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})

# Generate audio using gTTS
def generate_audio(text, output_path="static/output_audio.mp3"):
    # Ensure the static directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    tts = gTTS(text)
    tts.save(output_path)
    print(f"Audio file saved to: {output_path}")  # Add print statement to verify
    return output_path

# Function to split the sentence into segments
def split_sentence(sentence, max_words=8):
    words = sentence.split()
    segments = []
    for i in range(0, len(words), max_words):
        segment = ' '.join(words[i:i + max_words])
        segments.append(segment)
    return segments

# Function to create incremental text clips
def create_incremental_text_clip(text, duration, fontsize=40, color='red', bg_color='white', size=(1280, 720)):
    clips = []
    segment_duration = duration / len(text)

    for i in range(1, len(text) + 1):
        segment = text[:i]
        text_clip = TextClip(segment, fontsize=fontsize, color=color, bg_color=bg_color, size=size)
        text_clip = text_clip.set_duration(segment_duration)
        clips.append(text_clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    return final_clip

# Route to handle input and output
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form["question"]
        answer = get_answer(question)
        
        if answer:
            try:
                generated_text = answer['candidates'][0]['content']['parts'][0]['text']
                cleaned_answer = clean_text(generated_text)
                print("Generated Text:", cleaned_answer)

                # Generate audio and video
                audio_path = generate_audio(cleaned_answer)
                audio_clip = AudioFileClip(audio_path)
                audio_duration = audio_clip.duration

                segments = split_sentence(cleaned_answer, max_words=8)

                total_duration = audio_duration
                clips = []
                for segment in segments:
                    segment_clip = create_incremental_text_clip(segment, duration=total_duration / len(segments))
                    clips.append(segment_clip)

                final_text_clip = concatenate_videoclips(clips, method="compose")

                if final_text_clip.duration < audio_duration:
                    final_text_clip = concatenate_videoclips([final_text_clip] * int(audio_duration // final_text_clip.duration + 1))
                    final_text_clip = final_text_clip.subclip(0, audio_duration)
                elif final_text_clip.duration > audio_duration:
                    final_text_clip = final_text_clip.subclip(0, audio_duration)

                final_video_with_audio = final_text_clip.set_audio(audio_clip)

                final_output_path = "static/output_video.mp4"
                final_video_with_audio.write_videofile(final_output_path, codec='libx264', audio_codec='aac', fps=24, audio_fps=44100)

                print(f"The final video with synchronized text and audio has been created successfully! Saved as {final_output_path}")
                return render_template("index.html", question=question, generated_text=cleaned_answer, audio_path=audio_path, video_path=final_output_path)

            except (IndexError, KeyError):
                return "No text generated or unexpected response structure."
    
    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
