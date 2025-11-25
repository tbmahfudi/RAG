"""Text chunking utilities"""

from typing import List, Dict


def split_text_into_chunks(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[str]:
    """
    Split text into chunks using recursive character splitting.

    This function tries to split text on natural boundaries (paragraphs, sentences)
    before falling back to character-based splitting.

    Args:
        text: The text to split
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # If text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    separators = ["\n\n", "\n", ". ", " ", ""]

    def split_recursive(text: str, separators: List[str]) -> List[str]:
        """Recursively split text using the separator hierarchy"""
        if not separators:
            # Last resort: split by character
            return [
                text[i : i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)
            ]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            # Split by character
            return [
                text[i : i + chunk_size] for i in range(0, len(text), chunk_size - chunk_overlap)
            ]

        # Split by current separator
        splits = text.split(separator)
        current_chunks = []
        current_chunk = ""

        for split in splits:
            # Add separator back (except for last split)
            test_chunk = current_chunk + (separator if current_chunk else "") + split

            if len(test_chunk) <= chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full
                if current_chunk:
                    current_chunks.append(current_chunk)

                # If single split is too large, recursively split it
                if len(split) > chunk_size:
                    sub_chunks = split_recursive(split, remaining_separators)
                    current_chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = split

        # Add remaining chunk
        if current_chunk:
            current_chunks.append(current_chunk)

        return current_chunks

    # Perform recursive splitting
    initial_chunks = split_recursive(text, separators)

    # Add overlap between chunks
    for i, chunk in enumerate(initial_chunks):
        if i == 0:
            chunks.append(chunk)
        else:
            # Get overlap from previous chunk
            prev_chunk = initial_chunks[i - 1]
            overlap_text = prev_chunk[-chunk_overlap:] if len(prev_chunk) > chunk_overlap else prev_chunk
            chunks.append(overlap_text + " " + chunk)

    return chunks


def create_chunk_metadata(
    chunks: List[str], document_id: str, filename: str, file_type: str
) -> List[Dict]:
    """
    Create metadata for each chunk.

    Args:
        chunks: List of text chunks
        document_id: Unique document identifier
        filename: Original filename
        file_type: File type (pdf, txt)

    Returns:
        List of dictionaries containing chunk text and metadata
    """
    chunk_data = []

    for i, chunk_text in enumerate(chunks):
        chunk_data.append(
            {
                "text": chunk_text,
                "metadata": {
                    "document_id": document_id,
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            }
        )

    return chunk_data
