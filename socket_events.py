import logging
from flask_socketio import emit, join_room, leave_room
from game import GameManager

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

game_manager = GameManager()


def handle_join(data, socketio):
    action = data.get('action')
    room = data.get('room')

    if action == 'start':
        room = game_manager.create_game()
        logger.info(f"New game created with room ID: {room}")
        emit('room_created', {'room': room})
        emit('assign_player', {'assignedPlayer': 'X'})
        join_room(room)
    elif action == 'join':
        if not room or not game_manager.get_game(room):
            emit('error', {'message': 'Invalid room ID or room does not exist'})
            return
        game = game_manager.get_game(room).get('game')
        players = game.players
        player = 'X' if len(players) == 0 else 'O'
        game.add_player(player)
        emit('assign_player', {'assignedPlayer': player})
        join_room(room)
    else:
        emit('error', {'message': 'Invalid action'})

    if room:
        game = game_manager.get_game(room).get('game')
        emit('update', {'board': game.board, 'turn': game.turn, 'room': room}, room=room)


def handle_move(data, socketio):
    room = data['room']
    row, col = int(data['row']), int(data['col'])
    player = data['player']
    game = game_manager.get_game(room)

    if game and game['game'].board[row][col] is None and game['game'].turn == player:
        game['game'].board[row][col] = player
        winner = game['game'].check_winner()
        if winner or all(cell is not None for row in game['game'].board for cell in row):
            socketio.emit('update', {'turn': game['game'].turn, 'board': game['game'].board, 'room': room}, room=room)
            socketio.emit('game_over', {'winner': winner, 'room': room}, room=room)
            game_manager.reset_game(room)
        else:
            game['game'].turn = 'O' if game['game'].turn == 'X' else 'X'
        socketio.emit('update', {'turn': game['game'].turn, 'board': game['game'].board, 'room': room}, room=room)
    else:
        logger.warning(f"Invalid move by player {player} at ({row}, {col}). Board: {game['game'].board}")


def cleanup_expired_rooms(socketio):
    game_manager.cleanup_expired_games(socketio)

