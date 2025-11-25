class UploadManager {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.progressContainer = document.getElementById('upload-progress');
        this.progressBarFill = document.getElementById('progress-bar-fill');
        this.uploadStatus = document.getElementById('upload-status');
        this.documentItems = document.getElementById('document-items');
        this.documentCount = document.getElementById('document-count');

        this.init();
    }

    init() {
        // Drag and drop handlers
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('border-primary', 'bg-blue-50');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('border-primary', 'bg-blue-50');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('border-primary', 'bg-blue-50');
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        // File input handler
        this.fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
            e.target.value = ''; // Reset input
        });

        // Click to select
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Load existing documents
        this.loadDocuments();
    }

    async handleFiles(files) {
        // Filter valid files
        const validFiles = files.filter(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            const valid = ['pdf', 'txt'].includes(ext) && file.size <= 10 * 1024 * 1024;

            if (!valid) {
                showToast(`Invalid file: ${file.name}`, 'error');
            }

            return valid;
        });

        if (validFiles.length === 0) return;

        // Show progress
        this.progressContainer.classList.remove('hidden');
        this.progressBarFill.style.width = '0%';
        this.uploadStatus.textContent = `Uploading ${validFiles.length} file(s)...`;

        try {
            // Upload files
            const result = await api.uploadDocuments(validFiles);

            // Update progress
            this.progressBarFill.style.width = '100%';

            // Show results
            const successCount = result.results.filter(r => r.success).length;
            const failCount = result.results.filter(r => !r.success).length;

            if (successCount > 0) {
                showToast(`Successfully uploaded ${successCount} document(s)`, 'success');
            }

            if (failCount > 0) {
                result.results
                    .filter(r => !r.success)
                    .forEach(r => showToast(`Failed: ${r.filename} - ${r.error}`, 'error'));
            }

            // Reload document list
            await this.loadDocuments();

            // Enable chat if documents exist
            if (successCount > 0) {
                document.getElementById('chat-input').disabled = false;
                document.getElementById('send-btn').disabled = false;
            }

        } catch (error) {
            showToast(`Upload failed: ${error.message}`, 'error');
        } finally {
            // Hide progress after delay
            setTimeout(() => {
                this.progressContainer.classList.add('hidden');
            }, 2000);
        }
    }

    async loadDocuments() {
        try {
            const data = await api.getDocuments();

            if (data.total === 0) {
                this.documentItems.innerHTML = '<p class="text-gray-500 text-center py-8">No documents uploaded yet</p>';
                this.documentCount.textContent = '0 documents loaded';
                return;
            }

            // Render documents
            this.documentItems.innerHTML = data.documents.map(doc => `
                <div class="bg-gray-50 p-3 rounded-lg">
                    <div class="font-medium text-gray-800">📄 ${doc.filename}</div>
                    <div class="text-xs text-gray-600 mt-1">
                        ${doc.chunks_count} chunks • ${this.formatFileSize(doc.file_size)}
                    </div>
                </div>
            `).join('');

            this.documentCount.textContent = `${data.total} document(s) loaded`;

            // Enable chat input if documents exist
            if (data.total > 0) {
                document.getElementById('chat-input').disabled = false;
                document.getElementById('send-btn').disabled = false;
            }

        } catch (error) {
            console.error('Failed to load documents:', error);
        }
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
}
