document.addEventListener('DOMContentLoaded', function() {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const playMusicBtn = document.getElementById('play-music');
    const changeMusicBtn = document.getElementById('change-music');
    const spotifyPlayer = document.getElementById('spotify-player');

    let sessionId = 'user_' + Date.now();

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + sender;
        messageDiv.textContent = text;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        addMessage(query, 'user');
        userInput.value = '';

        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query, session_id: sessionId }),
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Lo siento, hubo un error. Inténtalo de nuevo.', 'bot');
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Música
    let playlists = [
        'https://open.spotify.com/embed/playlist/37i9dQZF1DX0XUsuxWHRQd', // Ambiente
        'https://open.spotify.com/embed/playlist/37i9dQZF1DX4PP3DA4J0N8', // Jazz
        'https://open.spotify.com/embed/playlist/37i9dQZF1DX4E3UdUs7fUx'  // Clásica
    ];
    let currentPlaylist = 0;

    playMusicBtn.addEventListener('click', function() {
        spotifyPlayer.style.display = 'block';
        playMusicBtn.textContent = 'Pausar Música';
        // Nota: El iframe maneja autoplay, pero puede requerir interacción del usuario
    });

    changeMusicBtn.addEventListener('click', function() {
        currentPlaylist = (currentPlaylist + 1) % playlists.length;
        spotifyPlayer.src = playlists[currentPlaylist];
    });
});