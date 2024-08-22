import threading
import time
from typing import Literal
from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from S3Manager import S3Manager
from SpeechToTextConverter import SpeechToTextConverter
from TextToSpeechConverter import TextToSpeechConverter

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

OPENAI_API_KEY = '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'


class PodcastBot:
    def __init__(self, update_client):
        self.__audio_manager = AudioManager("background_music.wav", update_client)
        self.__openai_manager = OpenAIManager(OPENAI_API_KEY)
        self.__speech_to_text_converter = SpeechToTextConverter(self.__audio_manager, self.__openai_manager)
        self.__text_to_speech_converter = TextToSpeechConverter(self.__audio_manager, self.__openai_manager,
                                                                update_client)
        self.__s3_manager = S3Manager(bucket_name="podcast-bot")
        self.__in_session = False
        self.update_client = update_client

    def upload_file_in_background(self, output_file_path, output_folder_key):
        try:
            self.__s3_manager.upload_file(output_file_path, output_folder_key)
        except Exception as e:
            print("Error during upload:", e)

    def run_bot(self, output_file_path, timestamp):
        self.__in_session = True
        try:
            self.update_client("loading")
            output_folder_key = self.__s3_manager.create_folder(timestamp)
            # self.__audio_manager.play_audio_file("get_name.wav")
            self.__text_to_speech_converter.generate_audio("Hello dear. welcome to the Jerusalem Design Week. We'll "
                                                           "start our recording very soon. Please remember to speak "
                                                           "in English, slowly and clearly. Before we begin, can I ask "
                                                           "what is your name?")
            self.update_client("listening")
            name = self.__speech_to_text_converter.speech_to_text(lng='he')
            # self.__audio_manager.play_audio_file("get_topic.wav")
            self.update_client("loading")
            self.__text_to_speech_converter.generate_audio(f"Now, which topic should we discuss in our podcast "
                                                           f"episode today? I'll give you a moment to think about it.")
            self.update_client("loading")
            time.sleep(5)
            self.update_client("listening")
            topic = self.__speech_to_text_converter.speech_to_text()
            self.update_client("loading")
            self.__text_to_speech_converter.stream_generated_audio(
                f"Very shortly introduce a podcast episode about the topic: {topic}. "
                f"Shortly introduce your interviewee named {name}. Ask a general opinion question related the topic")
            self.update_client("listening")
            discussion = self.__speech_to_text_converter.speech_to_text()
            self.update_client("loading")
            self.__text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                                   f"as respone to his\her previous answer: {discussion}")
            self.update_client("listening")
            discussion_2 = self.__speech_to_text_converter.speech_to_text()
            self.update_client("loading")
            self.__text_to_speech_converter.stream_generated_audio(f"ask your interviewer a follow up question"
                                                                   f"as respone to his\her previous answer: {discussion_2}")
            self.update_client("listening")
            self.__speech_to_text_converter.speech_to_text()
            self.update_client("loading")
            self.__text_to_speech_converter.stream_generated_audio(f"Say goodbye and thanks to {name} for being here")
            self.update_client("loading")
            self.__audio_manager.combine_audio_files(output_path=output_file_path)
            upload_thread = threading.Thread(target=self.upload_file_in_background,
                                             args=(output_file_path, output_folder_key))
            upload_thread.start()
            self.__audio_manager.play_audio_file(output_file_path, "playing")
            upload_thread.join()
            self.update_client("done")
        except Exception as e:
            print("Error: ", e)
        finally:
            self.__in_session = False
            print("Session ended")

    def get_recording_url(self, file_path, folder_key):
        return self.__s3_manager.get_recording_url(file_path, folder_key)

    def in_session(self):
        return self.__in_session
