const socket = io();
let room = null;
let player = null;

function startNewGame() {
    room = null;  // Clear the room ID
    socket.emit('join', { action: 'start' });
}

function joinGame() {
    room = document.getElementById('roomIdInput').value;
    if (!room) {
        alert('Please enter a room ID');
        return;
    }
    socket.emit('join', { action: 'join', room });
}

function displayRoomId(id) {
    document.getElementById('roomIdText').innerText = id;
    document.getElementById('roomIdDisplay').style.display = 'block';
}

function copyRoomId() {
    const roomIdText = document.getElementById('roomIdText');
    const range = document.createRange();
    range.selectNode(roomIdText);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand('copy');
    // alert('Room ID copied to clipboard');
}

socket.on('room_created', (data) => {
    console.log('Room created:', data);
    room = data.room;
    displayRoomId(room);
});

socket.on('assign_player', (data) => {
    console.log('Player assigned:', data);
    player = data.assignedPlayer;
    alert(`You are player ${player}`);
});

socket.on('update', (data) => {
    console.log('Board update:', data);
    const board = data.board;
    const turn = data.turn;
    document.querySelectorAll('td').forEach(td => {
        const row = td.getAttribute('data-row');
        const col = td.getAttribute('data-col');
        td.innerText = board[row][col] ? board[row][col] : '';
        td.style.pointerEvents = (!board[row][col] && turn === player) ? 'auto' : 'none';
    });
});

socket.on('game_over', (data) => {
    console.log('Game over:', data);
    alert(data.winner ? `${data.winner} wins!` : 'Draw!');
});

document.querySelectorAll('td').forEach(td => {
    td.addEventListener('click', () => {
        if (player) {
            const row = td.getAttribute('data-row');
            const col = td.getAttribute('data-col');
            console.log('player is:', player);
            socket.emit('move', { room, row, col, player });
        }
    });
});

socket.on('room_expired', (data) => {
    alert(data.message);
    // Optionally, reset the game or navigate the player to a different page
});


socket.on('error', (data) => {
    alert(data.message);
});
