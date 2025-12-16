import os
from google.cloud import texttospeech
from datetime import datetime
import asyncio
# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
async def sythesize_long_audio():
    
# Instantiates a client
    client = texttospeech.TextToSpeechLongAudioSynthesizeAsyncClient()

    print(f"Starting audiobook generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    def read_md_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    markdown_text = read_md_file("out_md/meditations_for_mortals_es.cleaned_fixed.md")

    input_text = texttospeech.SynthesisInput(text=markdown_text)

    # Select the voice and language code.
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-US",  # for "voces en HD de Chirp 3"
        name="es-US-Chirp3-HD-Erinome",  # Replace with a specific voice name
    )

    # Select the type of audio file you want returned.
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    project_id = "minismallprojects"  # Replace with your GCP project ID
    parent = f"projects/{project_id}/locations/us-central1"

    request = texttospeech.SynthesizeLongAudioRequest(
        parent=parent,
        input=input_text,
        voice=voice,
        audio_config=audio_config,
        output_gcs_uri="gs://audio_generation_folder/meditations_for_mortals.mp3"  # Replace with your GCS bucket
    )

    operation = client.synthesize_long_audio(
        request=request
    )

    result = (await operation).result()

    print('Long audio content written to GCS bucket "audio_generation_folder" as "meditations_for_mortals.mp3"')

if __name__ == "__main__":
    asyncio.run(sythesize_long_audio())