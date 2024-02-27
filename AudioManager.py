import io

import pyaudio
import wave
import soundfile as sf


class AudioManager:
    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def __del__(self):
        self.audio.terminate()

    def record_to_wav_file(self, file_path, record_seconds=5, chunk=1024, channels=1, rate=44100) -> None:
        stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=channels,
                                 rate=rate,
                                 input=True,
                                 frames_per_buffer=chunk)
        print("Recording...")
        frames = []
        for i in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)
        print("Finished recording.")
        stream.stop_stream()
        stream.close()

        wf = wave.open(file_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def play_audio_file(self, audio_file_path) -> None:
        if audio_file_path:
            with sf.SoundFile(audio_file_path, 'r') as sound_file:
                stream = self.audio.open(format=pyaudio.paInt16, channels=sound_file.channels,
                                         rate=sound_file.samplerate,
                                         output=True)
                data = sound_file.read(1024, dtype='int16')

                while len(data) > 0:
                    stream.write(data.tobytes())
                    data = sound_file.read(102, dtype='int16')

                stream.stop_stream()
                stream.close()

    def play_stream_audio(self, iterator) -> None:
        buffer = io.BytesIO()
        for chunk in iterator.iter_content(chunk_size=4096):
            buffer.write(chunk)

        buffer.seek(0)

        with sf.SoundFile(buffer, 'r') as sound_file:
            channels = sound_file.channels
            rate = sound_file.samplerate

            stream = self.audio.open(format=pyaudio.paInt16, channels=channels, rate=rate, output=True)
            chunk_size = 1024
            data = sound_file.read(chunk_size, dtype='int16')

            while len(data) > 0:
                stream.write(data.tobytes())
                data = sound_file.read(chunk_size, dtype='int16')

            stream.stop_stream()
            stream.close()
