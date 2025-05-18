document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const resetButton = document.getElementById('reset-button');
    const typingIndicator = document.getElementById('typing-indicator');
    
    // Hide typing indicator initially
    typingIndicator.style.display = 'none';
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    resetButton.addEventListener('click', resetChat);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Initial greeting message
    addMessage('Olá! Eu sou Eve, sua assistente de IA. Como posso ajudar você hoje?', 'ai');
    
    // Function to send user message
    function sendMessage() {
        const message = messageInput.value.trim();
        
        // Don't send empty messages
        if (!message) {
            return;
        }
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input field
        messageInput.value = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        scrollToBottom();
        
        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Resposta da rede não foi ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Simulate a small delay for a more natural conversation flow
            setTimeout(() => {
                addMessage(data.response, 'ai');
            }, 500);
        })
        .catch(error => {
            console.error('Erro:', error);
            
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            // Show error message
            addMessage('Desculpe, ocorreu um erro ao processar sua solicitação.', 'ai');
        });
    }
    
    // Function to add a message to the chat
    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
        
        // Format links in text
        const formattedText = formatText(text);
        messageElement.innerHTML = formattedText;
        
        // Add message to chat container
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom of chat
        scrollToBottom();
    }
    
    // Function to format text (e.g., detect URLs and make them clickable)
    function formatText(text) {
        // Convert URLs to clickable links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const formattedText = text.replace(urlRegex, function(url) {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
        });
        
        // Convert newlines to <br> tags
        return formattedText.replace(/\n/g, '<br>');
    }
    
    // Function to scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Function to reset chat
    function resetChat() {
        // Show confirmation dialog
        if (confirm('Tem certeza que deseja reiniciar a conversa?')) {
            // Clear chat container
            while (chatContainer.firstChild) {
                chatContainer.removeChild(chatContainer.firstChild);
            }
            
            // Reset conversation on server
            fetch('/reset', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Chat reiniciado:', data);
                // Add initial greeting message
                addMessage('Olá! Eu sou Eve, sua assistente de IA. Como posso ajudar você hoje?', 'ai');
            })
            .catch(error => {
                console.error('Erro ao reiniciar o chat:', error);
            });
        }
    }
});
