from typing import Literal

from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from SpeechToTextConverter import SpeechToTextConverter
from TextToSpeechConverter import TextToSpeechConverter

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

OPENAI_API_KEY = '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'

if __name__ == '__main__':
    audio_manager = AudioManager("background_music.wav")
    openai_manager = OpenAIManager(OPENAI_API_KEY)
    speech_to_text_converter = SpeechToTextConverter(audio_manager, openai_manager)
    text_to_speech_converter = TextToSpeechConverter(audio_manager, openai_manager)

    text_to_speech_converter.generate_audio("Hello dear, what's your name?")
    name = speech_to_text_converter.speech_to_text(record_seconds=5)
    text_to_speech_converter.stream_generated_audio(f"Very shortly introduce a podcast episode about nothing. Also, say your interviewee's name {name}",
                                                    "You are a podcast host")
    topic = speech_to_text_converter.speech_to_text(record_seconds=5)
    text_to_speech_converter.stream_generated_audio(f"Say your opinion on the chosen topic: {topic}"
                                                    f"ask your interviewer a general opinion question related it.",
                                                    "You are a podcast host")
    discussion = speech_to_text_converter.speech_to_text(record_seconds=20)
    text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                    f"as respone to his\her previous answer: {discussion}",
                                                    "You are a podcast host")
    discussion = speech_to_text_converter.speech_to_text(record_seconds=20)
    text_to_speech_converter.stream_generated_audio(f"Say goodbye and thanks to {name} for being here",
                                                    "You are a podcast host")
    audio_manager.combine_audio_files()