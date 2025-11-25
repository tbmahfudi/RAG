class ChatManager {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');
        this.topKInput = document.getElementById('top-k');
        this.temperatureInput = document.getElementById('temperature');

        this.conversationId = null;
        this.isStreaming = false;

        this.init();
    }

    init() {
        // Send button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send (Shift+Enter for new line)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();

        if (!message || this.isStreaming) return;

        // Clear input
        this.chatInput.value = '';

        // Remove welcome message if exists
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();

        // Add user message
        this.addUserMessage(message);

        // Disable input
        this.setInputState(false);
        this.isStreaming = true;

        // Show typing indicator
        const typingId = this.addTypingIndicator();

        try {
            // Get settings
            const topK = parseInt(this.topKInput.value);
            const temperature = parseFloat(this.temperatureInput.value);

            // Start streaming
            await this.streamResponse(message, topK, temperature, typingId);

        } catch (error) {
            this.removeMessage(typingId);
            showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.setInputState(true);
            this.isStreaming = false;
        }
    }

    streamResponse(message, topK, temperature, typingId) {
        return new Promise((resolve, reject) => {
            const eventSource = api.createStreamingConnection(
                message,
                this.conversationId,
                topK,
                temperature
            );

            let aiMessageId = null;
            let fullResponse = '';
            let sources = [];

            eventSource.addEventListener('start', (e) => {
                const data = JSON.parse(e.data);
                this.conversationId = data.conversation_id;
                sources = data.sources;

                // Remove typing indicator and add AI message
                this.removeMessage(typingId);
                aiMessageId = this.addAIMessage('', sources);
            });

            eventSource.addEventListener('token', (e) => {
                const data = JSON.parse(e.data);
                fullResponse += data.token;
                this.updateAIMessage(aiMessageId, fullResponse, sources);
            });

            eventSource.addEventListener('done', (e) => {
                eventSource.close();
                resolve();
            });

            eventSource.addEventListener('error', (e) => {
                eventSource.close();

                if (e.data) {
                    try {
                        const data = JSON.parse(e.data);
                        reject(new Error(data.error));
                    } catch {
                        reject(new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8001'));
                    }
                } else {
                    // Network error - backend likely not running
                    reject(new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8001'));
                }
            });

            // Timeout after 60 seconds
            setTimeout(() => {
                eventSource.close();
                reject(new Error('Request timeout'));
            }, 60000);
        });
    }

    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-end mb-4 animate-fade-in';
        messageDiv.innerHTML = `
            <div class="bg-primary text-white px-4 py-3 rounded-lg max-w-[80%] break-words">
                ${this.escapeHtml(text)}
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAIMessage(text, sources = []) {
        const messageId = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-start mb-4 animate-fade-in';
        messageDiv.id = messageId;
        messageDiv.innerHTML = `
            <div class="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg max-w-[80%]">
                <div class="break-words">${this.escapeHtml(text)}</div>
                ${this.renderSources(sources)}
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        return messageId;
    }

    updateAIMessage(messageId, text, sources = []) {
        const messageDiv = document.getElementById(messageId);
        if (messageDiv) {
            messageDiv.innerHTML = `
                <div class="bg-gray-100 text-gray-800 px-4 py-3 rounded-lg max-w-[80%]">
                    <div class="break-words">${this.escapeHtml(text)}</div>
                    ${this.renderSources(sources)}
                </div>
            `;
            this.scrollToBottom();
        }
    }

    addTypingIndicator() {
        const messageId = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-start mb-4';
        messageDiv.id = messageId;
        messageDiv.innerHTML = `
            <div class="bg-gray-100 px-4 py-3 rounded-lg">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        return messageId;
    }

    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) message.remove();
    }

    renderSources(sources) {
        if (!sources || sources.length === 0) return '';

        return `
            <div class="mt-3 pt-3 border-t border-gray-300">
                <div class="text-sm font-semibold text-gray-700 mb-2">📚 Sources:</div>
                <div class="space-y-1">
                    ${sources.map(source => `
                        <div class="text-xs bg-white p-2 rounded">
                            <span class="font-medium text-primary">${source.filename}</span>
                            <span class="text-gray-500 ml-2">(${(source.similarity_score * 100).toFixed(0)}% match)</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    setInputState(enabled) {
        this.chatInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
