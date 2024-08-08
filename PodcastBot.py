import string
import threading
from datetime import datetime
from typing import Literal
from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from S3Manager import S3Manager
from SpeechToTextConverter import SpeechToTextConverter
from TextToSpeechConverter import TextToSpeechConverter

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

OPENAI_API_KEY = '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'


class PodcastBot:
    def __init__(self):
        self.__audio_manager = AudioManager("background_music.wav")
        self.__openai_manager = OpenAIManager(OPENAI_API_KEY)
        self.__speech_to_text_converter = SpeechToTextConverter(self.__audio_manager, self.__openai_manager)
        self.__text_to_speech_converter = TextToSpeechConverter(self.__audio_manager, self.__openai_manager)
        self.__s3_manager = S3Manager(bucket_name="podcast-bot")
        self.__in_session = False

    def upload_file_in_background(self, output_file_path, output_folder_key):
        try:
            self.__s3_manager.upload_file(output_file_path, output_folder_key)
        except Exception as e:
            print("Error during upload:", e)

    def run_bot(self, output_file_path, timestamp):
        self.__in_session = True
        try:
            output_folder_key = self.__s3_manager.create_folder(timestamp)
            self.__audio_manager.play_audio_file("get_name.wav")
            name = self.__speech_to_text_converter.speech_to_text()
            self.__audio_manager.play_audio_file("get_topic.wav")
            topic = self.__speech_to_text_converter.speech_to_text()
            self.__text_to_speech_converter.stream_generated_audio(
                f"Very shortly introduce a podcast episode about the topic: {topic}. "
                f"Shortly introduce your interviewee named {name}. Ask a general opinion question related the topic")
            discussion = self.__speech_to_text_converter.speech_to_text()
            self.__text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                                   f"as respone to his\her previous answer: {discussion}")
            discussion_2 = self.__speech_to_text_converter.speech_to_text()
            self.__text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                                   f"as respone to his\her previous answer: {discussion_2}")
            self.__speech_to_text_converter.speech_to_text()
            self.__text_to_speech_converter.stream_generated_audio(f"Say goodbye and thanks to {name} for being here")
            self.__audio_manager.combine_audio_files(output_path=output_file_path)
            upload_thread = threading.Thread(target=self.upload_file_in_background,
                                             args=(output_file_path, output_folder_key))
            upload_thread.start()
            self.__audio_manager.play_audio_file(output_file_path)
            upload_thread.join()
        except Exception as e:
            print("Error: ", e)
        finally:
            self.__in_session = False
            print("Session ended")

    def get_recording_url(self, file_path, folder_key):
        return self.__s3_manager.get_recording_url(file_path, folder_key)

    def in_session(self):
        return self.__in_session
