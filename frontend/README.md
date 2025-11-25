# RAG Chat Frontend

Pure JavaScript frontend for the RAG document Q&A system, styled with Tailwind CSS.

## Features

- 📤 **Drag & Drop Upload**: Upload multiple PDF/TXT files at once
- 💬 **Real-time Chat**: Streaming responses with Server-Sent Events
- 📚 **Source Citations**: View which documents were used for each answer
- 🎨 **Modern UI**: Beautiful interface with Tailwind CSS
- ⚡ **No Build Step**: Pure JavaScript, no frameworks or build tools

## Quick Start

### Option 1: Simple HTTP Server (Python)

```bash
cd frontend
python3 -m http.server 8081
```

### Option 2: Simple HTTP Server (Node.js)

```bash
npm install -g http-server
cd frontend
http-server -p 8081
```

### Option 3: Using nginx with Docker

See `docker-compose.yml` in the root directory.

Then open your browser to: `http://localhost:8081`

## Configuration

The API endpoint is configured in `js/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8001/api';
```

Change this if your backend is running on a different host/port.

## Project Structure

```
frontend/
├── index.html          # Main HTML page
├── js/
│   ├── api.js          # API client
│   ├── upload.js       # Upload handling
│   ├── chat.js         # Chat with streaming
│   └── app.js          # App initialization
├── assets/             # Images, icons, etc.
└── README.md
```

## How It Works

### 1. Document Upload
- Drag and drop or select multiple files
- Files are validated (PDF/TXT, max 10MB)
- Uploaded via multipart/form-data
- Progress shown with visual feedback
- Results displayed with success/error messages

### 2. Chat Interface
- Type questions about uploaded documents
- Responses stream in real-time using SSE
- Sources are displayed with similarity scores
- Adjustable parameters (top_k, temperature)

### 3. Streaming Flow
1. User sends message
2. Backend searches for relevant document chunks
3. Backend streams response tokens via SSE
4. Frontend updates UI in real-time
5. Sources displayed when complete

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported (requires EventSource API)

## Customization

### Change Colors
Edit the Tailwind config in `index.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#4a90e2',  // Change this
            }
        }
    }
}
```

### Modify API Settings
Edit `js/api.js` to change endpoints or add authentication headers.

### Add Features
The code is modular - each feature is in its own file:
- Upload logic: `js/upload.js`
- Chat logic: `js/chat.js`
- API calls: `js/api.js`

## Development

No build step required! Just edit the files and refresh your browser.

### Debugging
Open browser DevTools (F12) to:
- View console logs
- Inspect network requests
- Debug JavaScript

### Testing Streaming
The chat uses EventSource for SSE. You can test the stream endpoint directly:

```javascript
const source = new EventSource('http://localhost:8001/api/chat/stream?message=test');
source.addEventListener('token', (e) => console.log(e.data));
```

## Production Deployment

### Using nginx

Create `nginx.conf`:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Deploy:
```bash
docker run -p 80:80 -v $(pwd):/usr/share/nginx/html nginx:alpine
```

### Using Netlify/Vercel

Just drag and drop the `frontend` folder - it works as a static site!

## License

MIT
