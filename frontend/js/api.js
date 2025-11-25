// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// API client
const api = {
    // Upload multiple documents
    async uploadDocuments(files) {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return await response.json();
    },

    // Get all documents
    async getDocuments() {
        const response = await fetch(`${API_BASE_URL}/documents`);

        if (!response.ok) {
            throw new Error(`Failed to fetch documents: ${response.statusText}`);
        }

        return await response.json();
    },

    // Send chat message (non-streaming)
    async sendMessage(message, conversationId = null, topK = 5, temperature = 0.7) {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                conversation_id: conversationId,
                top_k: topK,
                temperature,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Chat failed');
        }

        return await response.json();
    },

    // Create EventSource for streaming
    createStreamingConnection(message, conversationId = null, topK = 5, temperature = 0.7) {
        const params = new URLSearchParams({
            message,
            top_k: topK,
            temperature,
        });

        if (conversationId) {
            params.append('conversation_id', conversationId);
        }

        return new EventSource(`${API_BASE_URL}/chat/stream?${params}`);
    },
};
