from typing import Literal

import pyaudio
import requests
import soundfile as sf
import io
from openai import OpenAI
import pygame

OPENAI_API_KEY = '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'
OPEN_API_SPEECH_URL = "https://api.openai.com/v1/audio/speech"
VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def get_pyaudio_format(subtype):
    if subtype == 'PCM_16':
        return pyaudio.paInt16
    return pyaudio.paInt16


def streamed_audio(input_text, model='tts-1', voice: VoiceType = 'nova'):
    headers = {
        "Authorization": f'Bearer {OPENAI_API_KEY}',  # Replace with your API key
    }
    data = {
        "model": model,
        "input": input_text,
        "voice": voice,
        "response_format": "opus",
    }

    audio = pyaudio.PyAudio()

    with requests.post(OPEN_API_SPEECH_URL, headers=headers, json=data, stream=True) as response:
        if response.status_code == 200:
            buffer = io.BytesIO()
            for chunk in response.iter_content(chunk_size=4096):
                buffer.write(chunk)

            buffer.seek(0)

            with sf.SoundFile(buffer, 'r') as sound_file:
                format = get_pyaudio_format(sound_file.subtype)
                channels = sound_file.channels
                rate = sound_file.samplerate

                stream = audio.open(format=format, channels=channels, rate=rate, output=True)
                chunk_size = 1024
                data = sound_file.read(chunk_size, dtype='int16')

                while len(data) > 0:
                    stream.write(data.tobytes())
                    data = sound_file.read(chunk_size, dtype='int16')

                stream.stop_stream()
                stream.close()
        else:
            print(f"Error: {response.status_code} - {response.text}")
        audio.terminate()


def play_mp3(file_path):
    pygame.mixer.init()  # Initialize the mixer module
    pygame.mixer.music.load(file_path)  # Load the MP3 file
    pygame.mixer.music.play()  # Play the music

    # Keep the script running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


if __name__ == '__main__':
    play_mp3("speech.mp3")
