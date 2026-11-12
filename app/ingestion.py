
from pathlib import Path
from pypdf import PdfReader


def extract_pdf_pages(pdf_path: Path):
    """
    Extract text from a PDF page by page.
    Preserve the original page number.
    """

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        text = text.strip()

        if text:
            pages.append({
                "document": pdf_path.name,
                "page": page_number,
                "text": text
            })

    return pages


def chunk_text(text: str, chunk_size: int = 500,
               overlap: int = 100):
    """
    Divide text into smaller overlapping chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    chunks = []

    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        # Avoid cutting a word when possible
        if end < len(text):
            whitespace = text.rfind(" ", start, end)

            if whitespace > start + chunk_size // 2:
                end = whitespace

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def create_chunks(pages, chunk_size=500, overlap=100):
    """
    Create chunks while preserving document and page metadata.
    """

    all_chunks = []

    for page in pages:

        text_chunks = chunk_text(
            page["text"],
            chunk_size,
            overlap
        )

        for chunk in text_chunks:

            all_chunks.append({
                "document": page["document"],
                "page": page["page"],
                "text": chunk
            })

    return all_chunks
