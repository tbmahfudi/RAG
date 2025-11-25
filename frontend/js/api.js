// API configuration
const API_BASE_URL = 'http://localhost:8001/api';

// API client
const api = {
    // Upload multiple documents
    async uploadDocuments(files) {
        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch(`${API_BASE_URL}/documents/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8001');
            }
            throw error;
        }
    },

    // Get all documents
    async getDocuments() {
        try {
            const response = await fetch(`${API_BASE_URL}/documents`);

            if (!response.ok) {
                if (response.status === 404) {
                    // No documents yet - return empty list
                    return { documents: [], total: 0 };
                }
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Failed to fetch documents: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8001');
            }
            throw error;
        }
    },

    // Send chat message (non-streaming)
    async sendMessage(message, conversationId = null, topK = 5, temperature = 0.7) {
        try {
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
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Chat failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Cannot connect to backend. Make sure the server is running on http://localhost:8001');
            }
            throw error;
        }
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
