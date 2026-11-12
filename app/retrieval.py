
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class Retriever:

    def __init__(
        self,
        index_path="storage/regulations.faiss",
        metadata_path="storage/metadata.json",
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):

        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        # Load FAISS index
        if not self.index_path.exists():
            raise FileNotFoundError(self.index_path)

        self.index = faiss.read_index(str(self.index_path))

        # Load metadata
        if not self.metadata_path.exists():
            raise FileNotFoundError(self.metadata_path)

        with open(self.metadata_path, "r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        # Ensure vectors and metadata match
        if self.index.ntotal != len(self.metadata):
            raise ValueError(
                "FAISS index and metadata have different sizes"
            )

    def search(self, query: str, top_k: int = 3):

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be positive")

        # Convert question into embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        )

        # Search FAISS index
        scores, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            # FAISS returns -1 when no result is available
            if idx == -1:
                continue

            chunk = self.metadata[idx]

            results.append({
                "document": chunk["document"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": float(score)
            })

        return results
