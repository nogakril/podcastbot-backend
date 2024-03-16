from flask import Flask, request, send_file
from AudioManager import AudioManager
from OpenAIManager import OpenAIManager
from TextToSpeechConverter import TextToSpeechConverter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = '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'


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.json
    input_text = data.get('input_text')
    if not input_text:
        return {"error": "No input text provided."}, 400
    audio_file_path = tts_converter.generate_audio(input_text)
    return send_file(audio_file_path, as_attachment=True)


@app.route('/stream_generated_audio', methods=['POST'])
def stream_generated_audio():
    data = request.json
    completion_input = data.get('completion_input')
    model_context = data.get('model_context')
    if not completion_input or not model_context:
        return {"error": "Completion input or model context not provided."}, 400
    tts_converter.stream_generated_audio(completion_input, model_context)
    return {"message": "Audio streaming initiated."}


if __name__ == '__main__':
    audio_manager = AudioManager("background_music.wav")
    openai_manager = OpenAIManager(OPENAI_API_KEY, "onyx")
    tts_converter = TextToSpeechConverter(audio_manager, openai_manager)
    app.run(debug=True)
