import os
from google.cloud import texttospeech

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

# Instantiates a client
client = texttospeech.TextToSpeechClient()

print("Starting audiobook generation...")

def read_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

markdown_text = read_md_file("out_md/meditations_for_mortals_es.md")

input_text = texttospeech.SynthesisInput(text=markdown_text)

# Select the voice and language code.
voice = texttospeech.VoiceSelectionParams(
    language_code="es-US",  # for "voces en HD de Chirp 3"
    name="es-US-Chirp3-HD-Erinome",  # Replace with a specific voice name
)

# Select the type of audio file you want returned.
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=input_text,
    voice=voice,
    audio_config=audio_config,
)

# The response's audio_content is binary.
with open("output_audio.mp3", "wb") as out:
    out.write(response.audio_content)
    print('Audio content written to file "output_audio.mp3"')