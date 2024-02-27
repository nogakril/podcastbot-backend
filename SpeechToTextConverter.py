import os
import tempfile

import AudioManager
import OpenAIManager


class SpeechToTextConverter:
    def __init__(self, audio_manager: AudioManager, openai_manager: OpenAIManager):
        self.__audio_manager = audio_manager
        self.__openai_manager = openai_manager

    # def speech_to_text(self, record_seconds=30) -> str:
    #     file_path = "output.wav"
    #     self.__audio_manager.record_to_wav_file(file_path=file_path, record_seconds=record_seconds)
    #     output = self.__openai_manager.generate_transcription_request(file_path=file_path)
    #     print("Recorded: ", output)
    #     return output

    def speech_to_text(self, record_seconds=30) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            temp_file_path = tmp_file.name
        self.__audio_manager.record_to_wav_file(file_path=temp_file_path, record_seconds=record_seconds)
        output = self.__openai_manager.generate_transcription_request(file_path=temp_file_path)
        print("Recorded: ", output)
        os.remove(temp_file_path)
        return output