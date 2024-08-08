import threading
from flask import Flask, request
from PodcastBot import PodcastBot
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

podcast_bot = PodcastBot()
OUTPUT_FILE_PATH = 'combined_audio.wav'


def run_bot_in_background(output_file_path, cur_time):
    podcast_bot.run_bot(output_file_path, cur_time)


@app.route('/run_session', methods=['GET'])
def run_session():
    cur_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if podcast_bot.in_session():
        return {"error": "The session is already in progress."}, 400
    thread = threading.Thread(target=run_bot_in_background, args=(OUTPUT_FILE_PATH, cur_time))
    thread.start()
    url = podcast_bot.get_recording_url(OUTPUT_FILE_PATH, f"recordings-{cur_time}/")
    return {"message": "Session started", "url": f"{url}"}, 200


if __name__ == '__main__':
    app.run(debug=True)
