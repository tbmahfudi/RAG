from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    TXT = "txt"


class DocumentUploadResponse(BaseModel):
    """Response for single document upload"""
    document_id: str
    filename: str
    file_type: FileType
    file_size: int  # bytes
    chunks_created: int
    uploaded_at: datetime


class UploadResult(BaseModel):
    """Result for a single file in batch upload"""
    success: bool
    filename: str
    document_id: Optional[str] = None
    file_type: Optional[FileType] = None
    file_size: Optional[int] = None
    chunks_created: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    error: Optional[str] = None


class MultiUploadResponse(BaseModel):
    """Response for multiple document uploads"""
    results: List[UploadResult]
    total_uploaded: int
    total_failed: int


class DocumentInfo(BaseModel):
    """Document information"""
    document_id: str
    filename: str
    file_type: FileType
    file_size: int
    chunks_count: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: List[DocumentInfo]
    total: int


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=10)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class Source(BaseModel):
    """Source reference for chat response"""
    chunk_id: str
    document_id: str
    filename: str
    content: str  # The actual chunk text
    similarity_score: float


class ChatResponse(BaseModel):
    """Chat response"""
    model_config = ConfigDict(protected_namespaces=())

    conversation_id: str
    answer: str
    sources: List[Source]
    model_used: str
    tokens_used: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
