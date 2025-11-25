"""Document processing service"""

import os
import uuid
from datetime import datetime
from typing import List, Tuple
from fastapi import UploadFile
from app.config import settings
from app.models.schemas import DocumentUploadResponse, FileType, UploadResult
from app.utils import extract_text_from_file, split_text_into_chunks
from app.utils.text_splitter import create_chunk_metadata
from app.services.vector_service import VectorService


class DocumentService:
    """Service for document upload and processing"""

    def __init__(self, vector_service: VectorService):
        """
        Initialize document service.

        Args:
            vector_service: Vector service instance
        """
        self.vector_service = vector_service

        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file.

        Args:
            file: Uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get file extension
        filename = file.filename or ""
        file_ext = filename.split(".")[-1].lower() if "." in filename else ""

        # Check file type
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            return False, f"File type '{file_ext}' not supported. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"

        # Note: File size will be checked during processing
        return True, ""

    async def process_single_document(
        self, file: UploadFile
    ) -> DocumentUploadResponse:
        """
        Process a single uploaded document.

        Args:
            file: Uploaded file

        Returns:
            DocumentUploadResponse with processing results

        Raises:
            ValueError: If file validation fails
            Exception: If processing fails
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        # Generate document ID
        document_id = str(uuid.uuid4())
        filename = file.filename or f"document_{document_id}"
        file_ext = filename.split(".")[-1].lower()
        uploaded_at = datetime.utcnow()

        # Save file to disk
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}_{filename}")

        try:
            # Read and save file
            content = await file.read()
            file_size = len(content)

            # Check file size
            max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_size:
                raise ValueError(
                    f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({settings.MAX_FILE_SIZE_MB}MB)"
                )

            with open(file_path, "wb") as f:
                f.write(content)

            # Extract text
            text = extract_text_from_file(file_path, file_ext)

            if not text:
                raise ValueError("No text could be extracted from the file")

            # Split into chunks
            chunks = split_text_into_chunks(
                text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP
            )

            # Create chunk metadata
            chunk_data = create_chunk_metadata(
                chunks, document_id, filename, file_ext
            )

            # Store in vector database
            document_metadata = {
                "filename": filename,
                "file_type": file_ext,
                "file_size": file_size,
                "uploaded_at": uploaded_at.isoformat(),
            }

            chunks_created = await self.vector_service.add_document_chunks(
                document_id, chunk_data, document_metadata
            )

            return DocumentUploadResponse(
                document_id=document_id,
                filename=filename,
                file_type=FileType(file_ext),
                file_size=file_size,
                chunks_created=chunks_created,
                uploaded_at=uploaded_at,
            )

        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

    async def process_multiple_documents(
        self, files: List[UploadFile]
    ) -> Tuple[List[UploadResult], int, int]:
        """
        Process multiple uploaded documents.

        Args:
            files: List of uploaded files

        Returns:
            Tuple of (results, success_count, failure_count)
        """
        results = []
        success_count = 0
        failure_count = 0

        for file in files:
            try:
                # Process document
                response = await self.process_single_document(file)

                # Success result
                results.append(
                    UploadResult(
                        success=True,
                        filename=response.filename,
                        document_id=response.document_id,
                        file_type=response.file_type,
                        file_size=response.file_size,
                        chunks_created=response.chunks_created,
                        uploaded_at=response.uploaded_at,
                    )
                )
                success_count += 1

            except Exception as e:
                # Failure result
                results.append(
                    UploadResult(
                        success=False, filename=file.filename or "unknown", error=str(e)
                    )
                )
                failure_count += 1

        return results, success_count, failure_count

    async def get_all_documents(self) -> List[dict]:
        """
        Get all documents from vector database.

        Returns:
            List of document metadata
        """
        return await self.vector_service.get_all_documents()
