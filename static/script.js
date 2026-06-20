document.addEventListener('DOMContentLoaded', function() {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

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

    // Radio en vivo (Streamtheworld)
    const radioSelect = document.getElementById('radio-select');
    const playRadioBtn = document.getElementById('play-radio');
    const radioPlayer = document.getElementById('radio-player');
    let isPlaying = false;

    playRadioBtn.addEventListener('click', function() {
        if (!isPlaying) {
            radioPlayer.src = radioSelect.value;
            radioPlayer.style.display = 'block';
            radioPlayer.play();
            playRadioBtn.textContent = '⏸ Detener';
            isPlaying = true;
        } else {
            radioPlayer.pause();
            playRadioBtn.textContent = '▶ Reproducir';
            isPlaying = false;
        }
    });

    radioSelect.addEventListener('change', function() {
        if (isPlaying) {
            radioPlayer.src = radioSelect.value;
            radioPlayer.play();
        }
    });
});