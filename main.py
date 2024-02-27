import pyaudio
import requests
import soundfile as sf
import io
import pygame
import threading, queue, tempfile
from openai import OpenAI, Stream
from typing import Literal, Optional, Union

from openai.types.chat import ChatCompletion, ChatCompletionChunk
from requests import Response

OPENAI_API_KEY = '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'
OPEN_API_SPEECH_URL = "https://api.openai.com/v1/audio/speech"
VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

audio_generation_queue = queue.Queue()
audio_playback_queue = queue.Queue()


def generate_audio_request(input_text, model, voice) -> Response:
    headers = {
        "Authorization": f'Bearer {OPENAI_API_KEY}',
    }
    data = {
        "model": model,
        "input": input_text,
        "voice": voice,
        "response_format": "opus",
    }
    response = requests.post(OPEN_API_SPEECH_URL, headers=headers, json=data, stream=True)
    return response


def stream_input_audio(input_text, model='tts-1', voice: VoiceType = 'nova') -> None:
    audio = pyaudio.PyAudio()
    response = generate_audio_request(input_text, model, voice)
    if response.status_code == 200:
        buffer = io.BytesIO()
        for chunk in response.iter_content(chunk_size=4096):
            buffer.write(chunk)

        buffer.seek(0)

        with sf.SoundFile(buffer, 'r') as sound_file:
            channels = sound_file.channels
            rate = sound_file.samplerate

            stream = audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, output=True)
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


def play_mp3(file_path) -> None:
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def generate_audio_file(input_text, model='tts-1', voice: VoiceType = 'nova') -> Optional[str]:
    response = generate_audio_request(input_text, model, voice)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.opus') as temp_file:
            for chunk in response.iter_content(chunk_size=4096):
                temp_file.write(chunk)
            return temp_file.name
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def play_audio_file(audio_file_path):
    if audio_file_path:
        with sf.SoundFile(audio_file_path, 'r') as sound_file:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=pyaudio.paInt16, channels=sound_file.channels, rate=sound_file.samplerate,
                                output=True)
            data = sound_file.read(1024, dtype='int16')

            while len(data) > 0:
                stream.write(data.tobytes())
                data = sound_file.read(102, dtype='int16')

            stream.stop_stream()
            stream.close()
            audio.terminate()


def process_audio_generation_queue():
    while True:
        input_text = audio_generation_queue.get()
        if input_text is None:
            break
        audio_file_path = generate_audio_file(input_text)
        audio_playback_queue.put(audio_file_path)
        audio_generation_queue.task_done()


def process_audio_playback_queue():
    while True:
        audio_file_path = audio_playback_queue.get()
        if audio_file_path is None:
            break
        play_audio_file(audio_file_path)
        audio_playback_queue.task_done()


def run_and_cleanup_queues():
    audio_generation_queue.join()
    audio_generation_queue.put(None)
    audio_playback_queue.join()
    audio_playback_queue.put(None)


def generate_completion_request(message, model_context, model) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": model_context},
            {"role": "user", "content": message},
        ],
        stream=True,
        temperature=0,
        max_tokens=500,
    )
    return completion


def completion_response_to_queue(message, model_context, model='gpt-3.5-turbo'):
    completion = generate_completion_request(message, model_context, model)
    sentence = ''
    sentences = []
    sentence_end_chars = {'.', '?', '!', '\n'}  # Split the chat's response

    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content is not None:
            for char in content:
                sentence += char
                if char in sentence_end_chars:
                    sentence = sentence.strip()
                    if sentence and sentence not in sentences:
                        sentences.append(sentence)
                        audio_generation_queue.put(sentence)
                        print(f"Queued sentence: {sentence}")  # Logging queued sentence
                    sentence = ''


def stream_generated_audio(completion_input, model_context):
    pygame.mixer.init()
    audio_generation_thread = threading.Thread(target=process_audio_generation_queue)
    audio_playback_thread = threading.Thread(target=process_audio_playback_queue)
    audio_generation_thread.start()
    audio_playback_thread.start()

    completion_response_to_queue(completion_input, model_context)
    run_and_cleanup_queues()

    audio_generation_thread.join()
    audio_playback_thread.join()
    pygame.mixer.quit()


if __name__ == '__main__':
    stream_generated_audio("how do you feel today?", "You are a friendly AI assistant.")
