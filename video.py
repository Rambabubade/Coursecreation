from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip
from moviepy.config import change_settings
from gtts import gTTS
import os

# Path to the ImageMagick executable
imagemagick_path = r"C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"
change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})

# Full sentence to display
full_sentence = "React is a popular JavaScript library for building dynamic user interfaces. Developed by Facebook, it excels in creating single-page applications."

# Generate audio using gTTS
def generate_audio(text, output_path="output(!).mp3"):
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

# Generate and verify audio file
audio_path = generate_audio(full_sentence)

# Load the generated audio clip and verify duration
audio_clip = AudioFileClip(audio_path)
print(f"Audio Duration: {audio_clip.duration} seconds")  # Verify audio duration
audio_duration = audio_clip.duration

# Split the full sentence into segments
segments = split_sentence(full_sentence, max_words=8)

# Create incremental text clips with the adjusted duration
total_duration = audio_duration
clips = []
for segment in segments:
    segment_clip = create_incremental_text_clip(segment, duration=total_duration / len(segments))
    clips.append(segment_clip)

# Concatenate all text clips into one video
final_text_clip = concatenate_videoclips(clips, method="compose")

# Ensure final video matches the duration of the audio
if final_text_clip.duration < audio_duration:
    final_text_clip = concatenate_videoclips([final_text_clip] * int(audio_duration // final_text_clip.duration + 1))
    final_text_clip = final_text_clip.subclip(0, audio_duration)
elif final_text_clip.duration > audio_duration:
    final_text_clip = final_text_clip.subclip(0, audio_duration)

# Set the audio of the final text clip to the generated audio
final_video_with_audio = final_text_clip.set_audio(audio_clip)

# Export the final video with audio and ensure proper fps and audio settings
final_output_path = "output(!).mp4"
final_video_with_audio.write_videofile(final_output_path, codec='libx264', audio_codec='aac', fps=24, audio_fps=44100)

print(f"The final video with synchronized text and audio has been created successfully! Saved as {final_output_path}")
