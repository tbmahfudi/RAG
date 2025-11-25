"""Vector database service using ChromaDB"""

import os

# Disable ChromaDB telemetry before importing chromadb
# This prevents telemetry errors from PostHog capture() method
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import openai
from app.config import settings
import uuid


class VectorService:
    """Service for managing vector embeddings and similarity search"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False,
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")

    async def add_document_chunks(
        self, document_id: str, chunks: List[Dict], metadata: Dict
    ) -> int:
        """
        Add document chunks to the vector database.

        Args:
            document_id: Unique document identifier
            chunks: List of chunk dictionaries with text and metadata
            metadata: Document-level metadata

        Returns:
            Number of chunks added
        """
        try:
            chunk_ids = []
            chunk_texts = []
            chunk_embeddings = []
            chunk_metadatas = []

            for chunk in chunks:
                # Generate unique chunk ID
                chunk_id = f"{document_id}_chunk_{chunk['metadata']['chunk_index']}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(chunk["text"])

                # Generate embedding
                embedding = await self.generate_embedding(chunk["text"])
                chunk_embeddings.append(embedding)

                # Combine document and chunk metadata
                combined_metadata = {
                    **metadata,
                    **chunk["metadata"],
                    "chunk_id": chunk_id,
                }
                chunk_metadatas.append(combined_metadata)

            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                documents=chunk_texts,
                metadatas=chunk_metadatas,
            )

            return len(chunks)

        except Exception as e:
            raise Exception(f"Failed to add chunks to vector DB: {str(e)}")

    async def search_similar_chunks(
        self, query: str, top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of similar chunks with metadata and scores
        """
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                return []

            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=top_k
            )

            # Format results
            similar_chunks = []
            for i in range(len(results["ids"][0])):
                similar_chunks.append(
                    {
                        "chunk_id": results["ids"][0][i],
                        "document_id": results["metadatas"][0][i]["document_id"],
                        "filename": results["metadatas"][0][i]["filename"],
                        "content": results["documents"][0][i],
                        "similarity_score": 1
                        - results["distances"][0][i],  # Convert distance to similarity
                        "metadata": results["metadatas"][0][i],
                    }
                )

            return similar_chunks

        except Exception as e:
            raise Exception(f"Failed to search vector DB: {str(e)}")

    async def get_all_documents(self) -> List[Dict]:
        """
        Get metadata for all documents in the collection.

        Returns:
            List of document metadata
        """
        try:
            # Get all items from collection
            if self.collection.count() == 0:
                return []

            results = self.collection.get()

            # Group by document_id
            documents = {}
            for i, metadata in enumerate(results["metadatas"]):
                doc_id = metadata["document_id"]

                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata["filename"],
                        "file_type": metadata["file_type"],
                        "file_size": metadata.get("file_size", 0),
                        "uploaded_at": metadata.get("uploaded_at", ""),
                        "chunks_count": 0,
                    }

                documents[doc_id]["chunks_count"] += 1

            return list(documents.values())

        except Exception as e:
            raise Exception(f"Failed to get documents: {str(e)}")

    def get_collection_count(self) -> int:
        """Get total number of chunks in collection"""
        return self.collection.count()
