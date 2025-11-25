# RAG FastAPI Application

A complete RAG (Retrieval-Augmented Generation) system with FastAPI backend and vanilla JavaScript frontend. Upload documents and ask questions using AI-powered chat with source citations.

## 🌟 Features

### Backend
- 📄 **Multiple Document Upload**: Batch upload PDF and TXT files
- 🔍 **Vector Search**: ChromaDB for efficient similarity search
- 🤖 **OpenAI Integration**: GPT-4o-mini for intelligent responses
- 💬 **Streaming Responses**: Real-time SSE (Server-Sent Events)
- 📊 **Source Citations**: Responses include relevant document excerpts
- ⚙️ **Configurable LLM**: Easy to switch between OpenAI models

### Frontend
- 🎨 **Modern UI**: Beautiful interface with Tailwind CSS
- 📤 **Drag & Drop**: Upload multiple files at once
- ⚡ **Real-time Updates**: Streaming chat responses
- 📱 **Responsive Design**: Works on desktop and mobile
- 🎯 **No Build Required**: Pure JavaScript, no frameworks

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- OpenAI API Key

### Option 1: Docker Compose (Recommended)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd RAG
   ```

2. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Edit `backend/.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8081
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend Setup

```bash
cd frontend

# Serve with Python
python -m http.server 8081

# Or with Node.js
npx http-server -p 8081
```

## 📁 Project Structure

```
RAG/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   │   └── routes.py     # Endpoints
│   │   ├── models/           # Pydantic models
│   │   │   └── schemas.py    # Data schemas
│   │   ├── services/         # Business logic
│   │   │   ├── vector_service.py      # ChromaDB operations
│   │   │   ├── document_service.py    # Document processing
│   │   │   └── chat_service.py        # RAG pipeline
│   │   ├── utils/            # Utilities
│   │   │   ├── file_parser.py         # PDF/TXT parsing
│   │   │   └── text_splitter.py       # Text chunking
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI app
│   ├── data/                 # Local storage (gitignored)
│   │   ├── uploads/          # Uploaded files
│   │   └── chromadb/         # Vector database
│   ├── tests/                # Unit tests
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── js/
│   │   ├── api.js            # API client
│   │   ├── upload.js         # Upload handling
│   │   ├── chat.js           # Chat with streaming
│   │   └── app.js            # Initialization
│   ├── index.html            # Main page
│   └── README.md
│
├── docker-compose.yml        # Docker orchestration
├── .env.example              # Environment template
├── .gitignore
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (with defaults)
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=5
MAX_FILE_SIZE_MB=10
```

### Backend Configuration

All settings in `backend/app/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model for chat |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Model for embeddings |
| `CHUNK_SIZE` | `1000` | Text chunk size (characters) |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks to retrieve |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |

## 📖 API Documentation

### Endpoints

#### Upload Documents
```http
POST /api/documents/upload
Content-Type: multipart/form-data

Body: files[] (multiple files)
```

#### List Documents
```http
GET /api/documents
```

#### Chat (Non-Streaming)
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Your question",
  "conversation_id": null,
  "top_k": 5,
  "temperature": 0.7
}
```

#### Chat (Streaming)
```http
GET /api/chat/stream?message=Your%20question&top_k=5&temperature=0.7
```

Full API documentation available at: http://localhost:8001/docs

## 🏗️ Architecture

### RAG Pipeline

```
User Question
    ↓
[1] Query Embedding (OpenAI)
    ↓
[2] Vector Search (ChromaDB)
    ↓
[3] Retrieve Top K Chunks
    ↓
[4] Build Context Prompt
    ↓
[5] LLM Generation (OpenAI)
    ↓
[6] Stream Response (SSE)
    ↓
Answer + Sources
```

### Document Processing Pipeline

```
Upload File(s)
    ↓
[1] Validate Type & Size
    ↓
[2] Extract Text (PyPDF2)
    ↓
[3] Split into Chunks
    ↓
[4] Generate Embeddings (OpenAI)
    ↓
[5] Store in ChromaDB
    ↓
Success Response
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### API Testing with curl

**Upload a document:**
```bash
curl -X POST http://localhost:8001/api/documents/upload \
  -F "files=@document.pdf"
```

**Chat:**
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the main topic?"}'
```

**Streaming chat:**
```bash
curl -N "http://localhost:8001/api/chat/stream?message=Hello"
```

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` files to version control
- **File Upload**: Validates file types and sizes
- **CORS**: Configure for production in `backend/app/main.py`
- **Rate Limiting**: Consider adding rate limits for production
- **Authentication**: Add JWT auth for multi-user deployments

## 🚢 Production Deployment

### Using Docker Compose

```bash
# Production build
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Setup

For production, update `docker-compose.yml`:
- Remove volume mount for hot reload
- Set `DEBUG=false`
- Configure proper CORS origins
- Add reverse proxy (nginx/traefik)
- Enable HTTPS

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8001/health
```

### Logs
```bash
# Docker
docker-compose logs -f backend

# Local
tail -f backend/app.log
```

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API errors**
- Check API key is correct in `.env`
- Verify you have credits in your OpenAI account
- Check rate limits

**2. Upload fails**
- Ensure file is PDF or TXT
- Check file size < 10MB
- Verify backend is running

**3. ChromaDB errors**
- Clear `backend/data/chromadb/` and restart
- Ensure write permissions on data directory

**4. CORS errors**
- Update `allow_origins` in `backend/app/main.py`
- Check frontend is served from allowed origin

## 🛣️ Roadmap

### Planned Features

- [ ] Document deletion
- [ ] Multi-user authentication
- [ ] Conversation history persistence
- [ ] Support for more file types (DOCX, MD, HTML)
- [ ] Hybrid search (vector + keyword)
- [ ] Re-ranking for better retrieval
- [ ] Multiple LLM providers (Anthropic, Gemini)
- [ ] Admin dashboard
- [ ] Usage analytics

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **OpenAI**: LLM and embeddings
- **ChromaDB**: Vector database
- **Tailwind CSS**: UI styling

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation in `backend/README.md` and `frontend/README.md`

---

**Built with ❤️ using FastAPI, OpenAI, and vanilla JavaScript**
