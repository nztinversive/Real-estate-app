document.addEventListener('DOMContentLoaded', function() {
    const chatbotContainer = document.getElementById('chatbot-container');
    const chatbotHeader = document.getElementById('chatbot-header');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Toggle chatbot visibility with smooth animation
    chatbotHeader.addEventListener('click', () => {
        chatbotContainer.classList.toggle('h-96');
        chatbotContainer.classList.toggle('h-12');
    });

    chatbotClose.addEventListener('click', () => {
        chatbotContainer.classList.add('h-12');
        chatbotContainer.classList.remove('h-96');
    });

    // Send message on button click or Enter key
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            showTypingIndicator();  // Show typing indicator

            console.log('Sending message:', message);  // Debug log

            // Send message to backend and get response
            fetch('/chatbot_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => {
                console.log('Response status:', response.status);  // Debug log
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);  // Debug log
                removeTypingIndicator();  // Remove typing indicator
                addMessage('bot', data.response);
            })
            .catch((error) => {
                console.error('Error:', error);
                removeTypingIndicator();  // Remove typing indicator
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            });
        }
    }

    function addMessage(sender, message) {
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const messageElement = document.createElement('div');
        const messageClass = sender === 'user' ? 'justify-end' : 'justify-start';
        const bubbleClass = sender === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-300 text-gray-800';

        messageElement.classList.add('flex', messageClass, 'mb-4');
        messageElement.innerHTML = `
            <div class="max-w-xs px-4 py-2 rounded-lg ${bubbleClass} relative">
                ${message}
                <span class="text-xs text-gray-500 absolute bottom-0 right-0 mr-2 mb-1">${timestamp}</span>
            </div>
        `;
        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.id = 'typing-indicator';
        typingElement.classList.add('flex', 'justify-start', 'mb-4');
        typingElement.innerHTML = `
            <div class="max-w-xs px-4 py-2 rounded-lg bg-gray-300 text-gray-800 relative">
                <span class="loader inline-block mr-2"></span>Bot is typing...
            </div>
        `;
        chatbotMessages.appendChild(typingElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            chatbotMessages.removeChild(typingElement);
        }
    }

    // Proactive message from the bot when the chatbot loads
    addMessage('bot', 'Hello! How can I assist you with your real estate investments today?');
});