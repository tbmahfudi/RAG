"""File parsing utilities for PDF and TXT files"""

import PyPDF2
from typing import Tuple


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content

    Raises:
        Exception: If PDF parsing fails
    """
    try:
        text_parts = []
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        full_text = "\n".join(text_parts)
        return full_text.strip()

    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.

    Args:
        file_path: Path to the TXT file

    Returns:
        File content

    Raises:
        Exception: If file reading fails
    """
    try:
        # Try UTF-8 first
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Fallback to latin-1
            with open(file_path, "r", encoding="latin-1") as file:
                return file.read().strip()

    except Exception as e:
        raise Exception(f"Failed to read TXT file: {str(e)}")


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extract text from a file based on its type.

    Args:
        file_path: Path to the file
        file_type: File extension (pdf or txt)

    Returns:
        Extracted text content

    Raises:
        ValueError: If file type is not supported
        Exception: If extraction fails
    """
    file_type = file_type.lower()

    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
