import threading
import time

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from PodcastBot import PodcastBot
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

OUTPUT_FILE_PATH = 'combined_audio.wav'


def update_client(state):
    socketio.emit('status_update', {'state': state}, namespace='/')


def run_bot_mock():
    for status in ['loading', 'listening', 'speaking', 'loading', 'playing', 'done']:
        update_client(status)
        time.sleep(3)


def run_bot_in_background(output_file_path, cur_time):
    podcast_bot.run_bot(output_file_path, cur_time)
    # run_bot_mock()
#

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
    podcast_bot = PodcastBot(update_client)
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
