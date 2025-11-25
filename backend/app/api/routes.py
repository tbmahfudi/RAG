"""API route definitions"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.models.schemas import (
    MultiUploadResponse,
    DocumentListResponse,
    ChatRequest,
    ChatResponse,
    ErrorResponse,
)
from app.services import VectorService, DocumentService, ChatService

# Create router
router = APIRouter(prefix="/api")

# Initialize services
vector_service = VectorService()
document_service = DocumentService(vector_service)
chat_service = ChatService(vector_service)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}


@router.post("/documents/upload", response_model=MultiUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents (PDF or TXT).

    Args:
        files: List of files to upload

    Returns:
        MultiUploadResponse with results for each file
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    try:
        results, success_count, failure_count = (
            await document_service.process_multiple_documents(files)
        )

        return MultiUploadResponse(
            results=results,
            total_uploaded=success_count,
            total_failed=failure_count,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents", response_model=DocumentListResponse)
async def get_documents():
    """
    Get list of all uploaded documents.

    Returns:
        DocumentListResponse with list of documents
    """
    try:
        documents = await document_service.get_all_documents()

        return DocumentListResponse(documents=documents, total=len(documents))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch documents: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message (non-streaming).

    Args:
        request: ChatRequest with message and parameters

    Returns:
        ChatResponse with answer and sources
    """
    try:
        # Check if there are any documents
        if vector_service.get_collection_count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No documents uploaded. Please upload documents first.",
            )

        response = await chat_service.generate_response(
            message=request.message,
            conversation_id=request.conversation_id,
            top_k=request.top_k,
            temperature=request.temperature,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/chat/stream")
async def chat_stream(
    message: str = Query(..., min_length=1, max_length=2000),
    conversation_id: Optional[str] = Query(None),
    top_k: int = Query(5, ge=1, le=10),
    temperature: float = Query(0.7, ge=0.0, le=2.0),
):
    """
    Send a chat message with streaming response (SSE).

    Args:
        message: User message
        conversation_id: Optional conversation ID
        top_k: Number of chunks to retrieve
        temperature: LLM temperature

    Returns:
        StreamingResponse with Server-Sent Events
    """
    try:
        # Check if there are any documents
        if vector_service.get_collection_count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No documents uploaded. Please upload documents first.",
            )

        return StreamingResponse(
            chat_service.stream_response(
                message=message,
                conversation_id=conversation_id,
                top_k=top_k,
                temperature=temperature,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")
