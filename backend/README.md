# RAG FastAPI Backend

FastAPI backend for RAG (Retrieval-Augmented Generation) document Q&A system.

## Features

- 📄 **Multiple Document Upload**: Upload PDF and TXT files (batch upload supported)
- 🔍 **Vector Search**: ChromaDB for efficient similarity search
- 🤖 **LLM Integration**: OpenAI GPT for intelligent responses
- 💬 **Streaming Chat**: Real-time streaming responses using SSE
- 📊 **Source Citations**: Responses include source references

## Tech Stack

- **FastAPI**: Modern web framework
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: LLM and embeddings API
- **PyPDF2**: PDF text extraction
- **Pydantic**: Data validation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

Open your browser to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```
GET /health
```

### Upload Documents
```
POST /api/documents/upload
Content-Type: multipart/form-data

Body: files[] (multiple files)
```

### List Documents
```
GET /api/documents
```

### Chat (Non-Streaming)
```
POST /api/chat
Content-Type: application/json

{
  "message": "Your question here",
  "conversation_id": null,
  "top_k": 5,
  "temperature": 0.7
}
```

### Chat (Streaming)
```
GET /api/chat/stream?message=Your%20question&top_k=5&temperature=0.7
```

## Docker Deployment

### Build Image
```bash
docker build -t rag-backend .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-your-key \
  -v $(pwd)/data:/app/data \
  rag-backend
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model for chat |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `1000` | Text chunk size (chars) |
| `CHUNK_OVERLAP` | `200` | Chunk overlap (chars) |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks to retrieve |
| `MAX_FILE_SIZE_MB` | `10` | Max upload file size |

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   ├── utils/            # Utilities
│   ├── config.py         # Configuration
│   └── main.py           # App entry point
├── data/                 # Local storage
│   ├── uploads/          # Uploaded files
│   └── chromadb/         # Vector DB
├── tests/                # Unit tests
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── .env.example         # Environment template
```

## Development

### Run Tests
```bash
pytest tests/
```

### Format Code
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## License

MIT
