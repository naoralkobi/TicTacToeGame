import uuid
import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Game:
    def __init__(self):
        self.board = [[None, None, None] for _ in range(3)]
        self.turn = 'X'
        self.players = []

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] is not None:
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] is not None:
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            return self.board[0][2]
        return None

    def reset(self):
        self.board = [[None, None, None] for _ in range(3)]
        self.turn = 'X'

    def add_player(self, player):
        self.players.append(player)

    @staticmethod
    def is_expired(expiry_time):
        """
        Check if the game has expired based on the given expiry_time.
        """
        return datetime.now() > expiry_time


class GameManager:
    def __init__(self):
        self.games = {}
        self.room_expiry_duration = timedelta(hours=1)

    def create_game(self):
        room_id = str(uuid.uuid4())  # Generate a unique room ID
        self.games[room_id] = {'game': Game(), 'created_at': datetime.now()}
        self.games[room_id].get('game').add_player('X')
        return room_id

    def get_game(self, room):
        return self.games.get(room, None)

    def reset_game(self, room):
        if room in self.games:
            self.games[room]['game'].reset()
            self.games[room]['created_at'] = datetime.now()

    def get_expired_rooms(self):
        return [room for room, data in self.games.items()
                if data['game'].is_expired(data['created_at'] + self.room_expiry_duration)]

    def cleanup_expired_games(self, socketio):
        """
        Remove games that have expired based on the room_expiry_duration.
        """
        expired_rooms = self.get_expired_rooms()
        for room in expired_rooms:
            logger.info(f"Removing expired game room: {room}")
            socketio.emit('room_expired', {'message': 'This game room has expired due to inactivity.'}, room=room)
            del self.games[room]
