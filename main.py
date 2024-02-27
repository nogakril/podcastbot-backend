

from typing import Literal

from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from SpeechToTextConverter import SpeechToTextConverter
from TextToSpeechConverter import TextToSpeechConverter

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

OPENAI_API_KEY = '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'


if __name__ == '__main__':
    audio_manager = AudioManager()
    openai_manager = OpenAIManager(OPENAI_API_KEY)
    speech_to_text_converter = SpeechToTextConverter(audio_manager, openai_manager)
    text_to_speech_converter = TextToSpeechConverter(audio_manager, openai_manager)
