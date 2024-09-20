from typing import Union
import requests
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from requests import Response

OPEN_API_SPEECH_URL = "https://api.openai.com/v1/audio/speech"


class OpenAIManager:
    def __init__(self, api_key, voice="nova"):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.voice = voice
        self.headers = {
            "Authorization": f'Bearer {self.api_key}',
        }

    def generate_audio_request(self, input_text) -> Response:
        data = {
            "model": "tts-1",
            "input": input_text,
            "voice": self.voice,
            "response_format": "wav",
        }
        response = requests.post(OPEN_API_SPEECH_URL, headers=self.headers, json=data, stream=True, timeout=5)
        if response.status_code == 200:
            return response
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def generate_completion_request(self, message, model_context) -> Union[
        ChatCompletion, Stream[ChatCompletionChunk]]:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": model_context},
                    {"role": "user", "content": message},
                ],
                stream=True,
                temperature=0,
                max_tokens=500,
                timeout=5
            )
        except Exception as e:  # This catches any other exceptions
            print("Caught an exception:", e)
            completion = ""
        return completion

    def generate_transcription_request(self, file_path, lng='en') -> str:
        audio_file = open(file_path, "rb")
        transcription = self.client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            language=lng,
            timeout=5
        )
        return transcription.text
