import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from socket_events import handle_join, handle_move, cleanup_expired_rooms
import threading
import time

# Configure logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('join')
def on_join(data):
    handle_join(data, socketio)


@socketio.on('move')
def on_move(data):
    handle_move(data, socketio)


def cleanup_task():
    while True:
        cleanup_expired_rooms(socketio)
        # Run cleanup every 5 minutes
        time.sleep(5 * 60)


if __name__ == '__main__':
    threading.Thread(target=cleanup_task, daemon=True).start()
    socketio.run(app, debug=True, host="0.0.0.0", port=5454, allow_unsafe_werkzeug=True)
