import AudioManager
import OpenAIManager


class SpeechToTextConverter:
    def __init__(self, audio_manager: AudioManager, openai_manager: OpenAIManager):
        self.audio_manager = audio_manager
        self.openai_manager = openai_manager

    def speech_to_text(self, record_seconds=30) -> str:
        file_path = "output.wav"
        self.audio_manager.record_to_wav_file(file_path=file_path, record_seconds=record_seconds)
        return self.openai_manager.generate_transcription_request(file_path=file_path)
