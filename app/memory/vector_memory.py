from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from openai import OpenAI


class SemanticMemory:
    """
    Lightweight FAISS-based semantic memory.

    Stores only meaningful reusable memories rather than
    every conversation message.
    """

    def __init__(
        self,
        index_path: str = "data/faiss_memory.index",
        metadata_path: str = "data/faiss_memory.json",
    ):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        self.client = None

        self.embedding_model = "text-embedding-3-small"

        self.dimension = 1536

        self.index = self._load_index()
        self.metadata = self._load_metadata()

    # ---------------------------------------------------------
    # Embedding
    # ---------------------------------------------------------

    def _embed(self, text: str) -> np.ndarray:
        if self.client is None:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )

        vector = np.array(
            response.data[0].embedding,
            dtype="float32",
        )

        # Normalize for cosine similarity using inner product.
        faiss.normalize_L2(vector.reshape(1, -1))

        return vector

    # ---------------------------------------------------------
    # Load / Save
    # ---------------------------------------------------------

    def _load_index(self):
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))

        return faiss.IndexFlatIP(self.dimension)

    def _load_metadata(self):
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []

        return []

    def _save(self):
        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        with open(
            self.metadata_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.metadata,
                f,
                indent=2,
                ensure_ascii=False,
            )

    # ---------------------------------------------------------
    # Add memory
    # ---------------------------------------------------------

    def add_memory(
        self,
        user_id: str,
        memory_text: str,
        memory_type: str = "preference",
        metadata: dict[str, Any] | None = None,
    ) -> None:

        if not memory_text.strip():
            return

        vector = self._embed(memory_text)

        self.index.add(vector.reshape(1, -1))

        self.metadata.append(
            {
                "user_id": user_id,
                "memory": memory_text,
                "memory_type": memory_type,
                "metadata": metadata or {},
            }
        )

        self._save()

    # ---------------------------------------------------------
    # Search memory
    # ---------------------------------------------------------

    def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 3,
        threshold: float = 0.55,
    ) -> list[dict[str, Any]]:

        if self.index.ntotal == 0:
            return []

        query_vector = self._embed(query)

        scores, indices = self.index.search(
            query_vector.reshape(1, -1),
            min(top_k, self.index.ntotal),
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx < 0:
                continue

            if score < threshold:
                continue

            memory = self.metadata[idx]

            # Do not return another user's memory.
            if memory.get("user_id") != user_id:
                continue

            results.append(
                {
                    "memory": memory.get("memory"),
                    "memory_type": memory.get("memory_type"),
                    "score": round(float(score), 3),
                    "metadata": memory.get("metadata", {}),
                }
            )

        return results

    # ---------------------------------------------------------
    # Clear user memory
    # ---------------------------------------------------------

    def clear_user(self, user_id: str) -> None:

        remaining = [
            item
            for item in self.metadata
            if item.get("user_id") != user_id
        ]

        self.metadata = remaining

        self.index = faiss.IndexFlatIP(self.dimension)

        for item in self.metadata:
            vector = self._embed(item["memory"])
            self.index.add(vector.reshape(1, -1))

        self._save()



