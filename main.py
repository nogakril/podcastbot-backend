import string
from datetime import datetime
from typing import Literal
from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from S3Manager import S3Manager
from SpeechToTextConverter import SpeechToTextConverter
from TextToSpeechConverter import TextToSpeechConverter

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

OPENAI_API_KEY = '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'

def run_bot():
    audio_manager = AudioManager("background_music.wav")
    openai_manager = OpenAIManager(OPENAI_API_KEY)
    speech_to_text_converter = SpeechToTextConverter(audio_manager, openai_manager)
    text_to_speech_converter = TextToSpeechConverter(audio_manager, openai_manager)

    while True:
        start_phrase = speech_to_text_converter.speech_to_text(False)
        start_phrase_no_punc = start_phrase.lower().translate(str.maketrans('', '', string.punctuation))
        print(start_phrase_no_punc)
        if start_phrase_no_punc in ["hello there", "im here"]:
            text_to_speech_converter.generate_audio("Hello dear, what's your name?")
            name = speech_to_text_converter.speech_to_text()
            text_to_speech_converter.generate_audio("Which topic should we discuss in our podcast episode today?")
            topic = speech_to_text_converter.speech_to_text()
            text_to_speech_converter.stream_generated_audio(
                f"Very shortly introduce a podcast episode about the topic: {topic}. "
                f"Shortly introduce your interviewee named {name}. Ask a general opinion question related the topic",
                "You are a podcast host")
            discussion = speech_to_text_converter.speech_to_text()
            text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                            f"as respone to his\her previous answer: {discussion}",
                                                            "You are a podcast host")
            discussion_2 = speech_to_text_converter.speech_to_text()
            # text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
            #                                                 f"as respone to his\her previous answer: {discussion_2}",
            #                                                 "You are a podcast host")
            # discussion_3 = speech_to_text_converter.speech_to_text()
            text_to_speech_converter.stream_generated_audio(f"Say goodbye and thanks to {name} for being here",
                                                            "You are a podcast host")
            audio_manager.combine_audio_files()


if __name__ == '__main__':
    # run_bot()
    s3_manager = S3Manager(bucket_name="podcast-bot")
    folder_key = s3_manager.create_folder()
    cur_time = datetime.now()
    print("Start time: ", cur_time)
    file_path = "combined_audio.wav"
    file_name = file_path.split("/")[-1]
    s3_manager.upload_file(file_path, folder_key)
    print("Time taken: ", datetime.now() - cur_time)
    print(s3_manager.get_recording_url(folder_key, file_name))
