import AudioManager
import OpenAIManager
import threading
import queue
import tempfile


class TextToSpeechConverter:
    def __init__(self, audio_manager: AudioManager, openai_manager: OpenAIManager):
        self.__audio_manager = audio_manager
        self.__openai_manager = openai_manager
        self.__audio_generation_queue = None
        self.__audio_playback_queue = None

    def _initialize_queues(self):
        self.__audio_generation_queue = queue.Queue()
        self.__audio_playback_queue = queue.Queue()

    def stream_generated_audio(self, completion_input, model_context="You are a podcast host") -> None:
        self._initialize_queues()
        audio_generation_thread = threading.Thread(target=self._process_audio_generation_queue)
        audio_playback_thread = threading.Thread(target=self._process_audio_playback_queue)
        audio_generation_thread.start()
        audio_playback_thread.start()
        self._completion_response_to_audio_queue(completion_input, model_context)
        self._run_and_cleanup_queues()
        audio_generation_thread.join()
        audio_playback_thread.join()

    def generate_audio(self, input_text) -> None:
        audio_file = self._generate_audio_file_from_text(input_text)
        self.__audio_manager.play_audio_file(audio_file)



    def _generate_audio_file_from_text(self, input_text) -> str:
        iterator = self.__openai_manager.generate_audio_request(input_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.opus') as temp_file:
            for chunk in iterator.iter_content(chunk_size=4096):
                temp_file.write(chunk)
        return temp_file.name

    def _process_audio_generation_queue(self) -> None:
        while True:
            input_text = self.__audio_generation_queue.get()
            if input_text is None:
                break
            audio_file_path = self._generate_audio_file_from_text(input_text)
            self.__audio_playback_queue.put(audio_file_path)
            self.__audio_generation_queue.task_done()

    def _process_audio_playback_queue(self) -> None:
        while True:
            audio_file_path = self.__audio_playback_queue.get()
            if audio_file_path is None:
                break
            self.__audio_manager.play_audio_file(audio_file_path)
            self.__audio_playback_queue.task_done()

    def _run_and_cleanup_queues(self) -> None:
        self.__audio_generation_queue.join()
        self.__audio_generation_queue.put(None)
        self.__audio_playback_queue.join()
        self.__audio_playback_queue.put(None)

    def _completion_response_to_audio_queue(self, message, model_context) -> None:
        completion = self.__openai_manager.generate_completion_request(message, model_context)
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
                            self.__audio_generation_queue.put(sentence)
                            print(f"Queued sentence: {sentence}")  # Logging queued sentence
                        sentence = ''
