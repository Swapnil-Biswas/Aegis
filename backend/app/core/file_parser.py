"""
Secure File Parser for Multi-Format Document Ingestion.
Supports TXT, PDF (pypdf), DOCX (python-docx), and Markdown with strict bounds checking.
"""

import io
import os
from typing import Tuple, Optional
from pypdf import PdfReader
import docx


class DocumentParserError(Exception):
    """Custom exception for document parsing failures."""
    pass


class DocumentParser:
    """
    Secure document parser with file-size limits, MIME validation,
    and memory-safe stream handling.
    """

    def __init__(self, max_size_bytes: int = 25 * 1024 * 1024):
        self.max_size_bytes = max_size_bytes

    def parse_txt(self, data: bytes) -> str:
        """Parses plain text with multi-encoding fallback."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def parse_pdf(self, data: bytes) -> str:
        """Extracts text from PDF streams using pypdf safely."""
        try:
            reader = PdfReader(io.BytesIO(data))
            text_parts = []
            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted.strip())
            
            if not text_parts:
                raise DocumentParserError("PDF contains no extractable text layer (may be scanned images or rasterized).")
            return "\n\n".join(text_parts)
        except Exception as e:
            if isinstance(e, DocumentParserError):
                raise
            raise DocumentParserError(f"Failed to parse PDF document: {str(e)}")

    def parse_docx(self, data: bytes) -> str:
        """Extracts text from DOCX packages using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(data))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)

            if not paragraphs:
                raise DocumentParserError("DOCX document contains no readable paragraph content.")
            return "\n\n".join(paragraphs)
        except Exception as e:
            if isinstance(e, DocumentParserError):
                raise
            raise DocumentParserError(f"Failed to parse DOCX document: {str(e)}")

    def parse(self, filename: str, data: bytes) -> Tuple[str, str]:
        """
        Parses uploaded file bytes based on file extension and magic byte verification.
        Returns: (extracted_text, detected_format)
        """
        if len(data) > self.max_size_bytes:
            raise DocumentParserError(
                f"File size ({len(data)} bytes) exceeds the allowed limit of {self.max_size_bytes} bytes."
            )

        ext = os.path.splitext(filename)[1].lower()

        if ext in [".txt", ".md", ".rtf"]:
            return self.parse_txt(data), "plaintext"
        elif ext == ".pdf":
            # PDF Magic bytes check: %PDF-
            if not data.startswith(b"%PDF"):
                raise DocumentParserError("Invalid PDF file header.")
            return self.parse_pdf(data), "pdf"
        elif ext == ".docx":
            # DOCX is a zip archive; magic bytes: PK\x03\x04
            if not data.startswith(b"PK\x03\x04"):
                raise DocumentParserError("Invalid DOCX file signature (corrupt or disguised format).")
            return self.parse_docx(data), "docx"
        else:
            # Fallback to UTF-8 text attempt
            return self.parse_txt(data), "plaintext_fallback"

