from typing import List, Dict, Tuple
import faiss
import numpy as np
import json
import os


class FAISSIndex:
    def __init__(
        self,
        embed_dim: int,
        index_path: str,
        meta_path: str,
        similarity_threshold: float = 0.5,
    ):
        self.embed_dim = embed_dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = faiss.IndexFlatIP(self.embed_dim)
        self.metadata: List[Dict] = []
        self.similarity_threshold = similarity_threshold
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, encoding="utf-8") as f:
                self.metadata = json.load(f)

    def add_embeddings(self, embeddings: np.ndarray, metadata: List[Dict]):
        self.index.add(embeddings)  # type: ignore
        self.metadata.extend(metadata)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)  # type: ignore
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if score >= self.similarity_threshold:  # Ensure valid distance
                results.append((idx, score))
        return results

    def generate_excerpts(self, relevant: List[Dict]) -> List[Tuple[str, Dict]]:
        excerpts = []
        seen_texts = set()
        for rank, (idx, score) in enumerate(relevant, start=1):
            m = self.metadata[idx]
            if (m["source"], m["chunk_id"]) not in seen_texts:
                seen_texts.add((m["source"], m["chunk_id"]))
                excerpts.append((m["text"], m))
        return excerpts

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f)
