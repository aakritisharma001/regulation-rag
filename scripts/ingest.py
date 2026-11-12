
import os
import json
from pathlib import Path

import faiss
import numpy as np

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from app.ingestion import extract_pdf_pages, create_chunks


# Load environment variables
load_dotenv()

PDF_DIR = Path("data/pdfs")
STORAGE_DIR = Path("storage")

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)


def main():

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        raise ValueError(
            "No PDF files found in data/pdfs"
        )

    all_pages = []

    # Step 1: Extract text from every PDF
    for pdf_path in pdf_files:

        print(f"Reading: {pdf_path.name}")

        pages = extract_pdf_pages(pdf_path)

        all_pages.extend(pages)

    if not all_pages:
        raise ValueError(
            "No extractable text found in the PDFs"
        )

    print(f"Extracted {len(all_pages)} pages")

    # Step 2: Create chunks
    chunks = create_chunks(
        all_pages,
        chunk_size=500,
        overlap=100
    )

    if not chunks:
        raise ValueError("No chunks were generated")

    print(f"Created {len(chunks)} chunks")

    # Step 3: Load embedding model
    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    # Step 4: Generate embeddings
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    print(f"Embedding shape: {embeddings.shape}")

    # Step 5: Create FAISS index
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    # Step 6: Save FAISS index
    faiss.write_index(
        index,
        str(STORAGE_DIR / "regulations.faiss")
    )

    # Step 7: Save metadata
    metadata_path = STORAGE_DIR / "metadata.json"

    with open(metadata_path, "w", encoding="utf-8") as file:

        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nIngestion completed successfully!")

    print(f"PDFs processed: {len(pdf_files)}")
    print(f"Pages extracted: {len(all_pages)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Vectors stored: {index.ntotal}")

    print("\nSaved files:")
    print("storage/regulations.faiss")
    print("storage/metadata.json")


if __name__ == "__main__":
    main()
