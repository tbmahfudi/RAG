from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App Settings
    APP_NAME: str = "RAG API MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")

    # OpenAI Models
    LLM_MODEL: str = "gpt-4o-mini"  # Cost-effective for MVP
    EMBEDDING_MODEL: str = "text-embedding-3-small"  # 1536 dimensions

    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    CHROMA_COLLECTION_NAME: str = "documents"

    # File Upload Settings
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "txt"]

    # Text Chunking
    CHUNK_SIZE: int = 1000  # characters
    CHUNK_OVERLAP: int = 200  # characters

    # RAG Settings
    RETRIEVAL_TOP_K: int = 5
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
