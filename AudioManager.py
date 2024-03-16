import pyaudio
import wave
import soundfile as sf
from pydub import AudioSegment
import webrtcvad
import time

class AudioManager:
    def __init__(self, music_file_path):
        self.audio = pyaudio.PyAudio()
        self.audio_files = []
        self.music_file_path = music_file_path
        self.recording_timeout = 120

    def __del__(self):
        self.audio.terminate()

    def record_to_wav_file_with_timer(self, file_path, record_seconds=5, chunk=1024, channels=1, rate=44100) -> None:
        if file_path:
            self.audio_files.append(file_path)
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

    def record_to_wav_file(self, file_path, save_file,  chunk=320, channels=1, rate=16000, silence_limit=1,
                           vad_aggressiveness=3):
        vad = webrtcvad.Vad(vad_aggressiveness)
        if file_path:
            if save_file:
                self.audio_files.append(file_path)
            stream = self.audio.open(format=pyaudio.paInt16,
                                     channels=channels,
                                     rate=rate,
                                     input=True,
                                     frames_per_buffer=chunk)
            print("Recording...")
            frames = []
            silence_frames = 0
            detected_speech = False
            start_time = time.time()


            while True:
                data = stream.read(chunk)
                frames.append(data)

                if vad.is_speech(data, rate):
                    detected_speech = True
                    silence_frames = 0
                else:
                    silence_frames += 1

                if detected_speech and silence_frames >= (silence_limit * rate) / chunk:
                    break

                if (time.time() - start_time) > self.recording_timeout:
                    print("Recording timeout reached, stopping recording.")
                    break

            print("Finished recording.")
            stream.stop_stream()
            stream.close()

            wf = wave.open(file_path, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            print(f"Recording saved: {file_path}")

    def play_audio_file(self, file_path) -> None:
        if file_path:
            self.audio_files.append(file_path)
            with sf.SoundFile(file_path, 'r') as sound_file:
                stream = self.audio.open(format=pyaudio.paInt16, channels=sound_file.channels,
                                         rate=sound_file.samplerate,
                                         output=True)
                data = sound_file.read(1024, dtype='int16')

                while len(data) > 0:
                    stream.write(data.tobytes())
                    data = sound_file.read(102, dtype='int16')

                stream.stop_stream()
                stream.close()

    def combine_audio_files(self, output_path="combined_audio.wav", fade_duration=3000, background_volume_dip=-15):
        combined = AudioSegment.empty()
        for file_path in self.audio_files[4:]:
            audio = AudioSegment.from_file(file_path, format="wav")
            combined += audio

        music = AudioSegment.from_file(self.music_file_path, format="wav")

        total_duration_with_pre_and_post = len(combined) + 2 * fade_duration

        pre_music = music[:fade_duration]
        during_podcast_music = music[fade_duration:len(combined) + fade_duration].apply_gain(background_volume_dip)
        post_music = music[len(combined) + fade_duration:total_duration_with_pre_and_post].fade_out(fade_duration)

        music_with_fades = pre_music + during_podcast_music + post_music

        final_mix = music_with_fades.overlay(combined, position=fade_duration)
        final_mix.export(output_path, format="wav")
        self.play_audio_file(output_path)
