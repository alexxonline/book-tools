from pathlib import Path

from book_tools.paths import output_path


def generate_audiobook(input_path, output=None, language="es-US", voice="es-US-Chirp3-HD-Erinome"):
    from google.cloud import texttospeech

    destination = output_path(input_path, output, extension=".mp3")
    client = texttospeech.TextToSpeechClient()
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=Path(input_path).read_text(encoding="utf-8")),
        voice=texttospeech.VoiceSelectionParams(language_code=language, name=voice),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3),
    )
    destination.write_bytes(response.audio_content)
    return destination


def generate_audiobook_long(input_path, project, output_gcs_uri, location="us-central1", language="es-US", voice="es-US-Chirp3-HD-Erinome", timeout=3600):
    from google.cloud import texttospeech

    if not output_gcs_uri.startswith("gs://") or not output_gcs_uri.endswith(".wav"):
        raise ValueError("Long audio requires a gs://bucket/path.wav output URI")
    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
    operation = client.synthesize_long_audio(request=texttospeech.SynthesizeLongAudioRequest(
        parent=f"projects/{project}/locations/{location}",
        input=texttospeech.SynthesisInput(text=Path(input_path).read_text(encoding="utf-8")),
        voice=texttospeech.VoiceSelectionParams(language_code=language, name=voice),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16),
        output_gcs_uri=output_gcs_uri,
    ))
    print(f"Waiting for operation: {operation.operation.name}")
    operation.result(timeout=timeout)
    return output_gcs_uri
