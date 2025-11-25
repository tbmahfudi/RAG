"""Chat service with RAG pipeline"""

import uuid
from typing import List, Dict, Optional, AsyncGenerator
import openai
import json
from app.config import settings
from app.models.schemas import Source, ChatResponse
from app.services.vector_service import VectorService


# System prompt for the assistant
SYSTEM_PROMPT = """You are a helpful AI assistant. Answer questions based on the provided context.

Rules:
- Only use information from the context
- If the answer is not in the context, say "I don't have enough information to answer that question based on the uploaded documents."
- Be concise and accurate
- Cite which document you're referencing when possible"""


class ChatService:
    """Service for RAG-based chat"""

    def __init__(self, vector_service: VectorService):
        """
        Initialize chat service.

        Args:
            vector_service: Vector service instance
        """
        self.vector_service = vector_service
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        """
        Build RAG prompt with retrieved context.

        Args:
            query: User question
            chunks: Retrieved chunks

        Returns:
            Formatted prompt
        """
        # Format context
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Document: {chunk['filename']}]\n{chunk['content']}"
            )

        context = "\n\n---\n\n".join(context_parts)

        # Build prompt
        prompt = f"""Context from uploaded documents:

{context}

Question: {query}

Answer:"""

        return prompt

    def format_sources(self, chunks: List[Dict]) -> List[Source]:
        """
        Format chunks as source references.

        Args:
            chunks: Retrieved chunks

        Returns:
            List of Source objects
        """
        sources = []
        for chunk in chunks:
            sources.append(
                Source(
                    chunk_id=chunk["chunk_id"],
                    document_id=chunk["document_id"],
                    filename=chunk["filename"],
                    content=chunk["content"][:200]
                    + "..."
                    if len(chunk["content"]) > 200
                    else chunk["content"],
                    similarity_score=chunk["similarity_score"],
                )
            )
        return sources

    async def generate_response(
        self,
        message: str,
        conversation_id: Optional[str],
        top_k: int,
        temperature: float,
    ) -> ChatResponse:
        """
        Generate RAG response (non-streaming).

        Args:
            message: User message
            conversation_id: Optional conversation ID
            top_k: Number of chunks to retrieve
            temperature: LLM temperature

        Returns:
            ChatResponse
        """
        # Generate or use conversation ID
        conv_id = conversation_id or str(uuid.uuid4())

        # Search for relevant chunks
        chunks = await self.vector_service.search_similar_chunks(message, top_k)

        if not chunks:
            return ChatResponse(
                conversation_id=conv_id,
                answer="I don't have any documents to reference. Please upload some documents first.",
                sources=[],
                model_used=settings.LLM_MODEL,
            )

        # Build prompt
        prompt = self.build_prompt(message, chunks)

        # Call OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=settings.LLM_MAX_TOKENS,
            )

            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            # Format sources
            sources = self.format_sources(chunks)

            return ChatResponse(
                conversation_id=conv_id,
                answer=answer or "",
                sources=sources,
                model_used=settings.LLM_MODEL,
                tokens_used=tokens_used,
            )

        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    async def stream_response(
        self,
        message: str,
        conversation_id: Optional[str],
        top_k: int,
        temperature: float,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming RAG response using Server-Sent Events.

        Args:
            message: User message
            conversation_id: Optional conversation ID
            top_k: Number of chunks to retrieve
            temperature: LLM temperature

        Yields:
            SSE formatted strings
        """
        try:
            # Generate or use conversation ID
            conv_id = conversation_id or str(uuid.uuid4())

            # Search for relevant chunks
            chunks = await self.vector_service.search_similar_chunks(message, top_k)

            if not chunks:
                # Send error event
                yield f"event: error\n"
                yield f'data: {json.dumps({"error": "No documents available"})}\n\n'
                return

            # Format sources
            sources = self.format_sources(chunks)

            # Send start event with sources
            yield f"event: start\n"
            yield f'data: {json.dumps({"conversation_id": conv_id, "sources": [s.model_dump() for s in sources]})}\n\n'

            # Build prompt
            prompt = self.build_prompt(message, chunks)

            # Stream from OpenAI
            stream = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=settings.LLM_MAX_TOKENS,
                stream=True,
            )

            # Forward tokens
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield f"event: token\n"
                    yield f'data: {json.dumps({"token": token})}\n\n'

            # Send completion event
            yield f"event: done\n"
            yield f'data: {json.dumps({"model": settings.LLM_MODEL})}\n\n'

        except Exception as e:
            # Send error event
            yield f"event: error\n"
            yield f'data: {json.dumps({"error": str(e)})}\n\n'
