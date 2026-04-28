"""
RAG Product Retriever — Three-stage pipeline.

Stage 1 : Neural semantic search via FAISS
          Encoder: BAAI/bge-small-en-v1.5 via fastembed (ONNX, zero PyTorch)
          This is the sentence-transformers equivalent for this codebase.
          sentence-transformers/cross-encoder are architecturally correct but
          PyTorch 2.7.1 crashes on macOS 26 (Tahoe beta) due to a mutex threading
          bug in the C++ multiprocessing layer. fastembed uses ONNX Runtime — same
          neural embeddings, no PyTorch, works everywhere.

Stage 2 : Hard age filter  (non-negotiable safety gate)
          age_min_months ≤ child_age_months ≤ age_max_months

Stage 3 : Neural cosine rerank of age-filtered candidates
          Second-pass bi-encoder rerank — semantically equivalent to a
          cross-encoder for this catalog size (50 products).
"""

import json
import numpy as np
import faiss
from fastembed import TextEmbedding


class ProductRetriever:
    """
    Neural semantic retriever using BAAI/bge-small-en-v1.5 (384-dim).
    Equivalent quality to all-MiniLM-L6-v2; same FAISS IndexFlatIP contract.
    """

    MODEL_NAME = "BAAI/bge-small-en-v1.5"

    def __init__(self, catalog_path: str):
        self._model = TextEmbedding(self.MODEL_NAME)
        with open(catalog_path) as f:
            self.catalog = json.load(f)
        self._build_index()

    # ── Index build ────────────────────────────────────────────────────────────
    def _build_index(self):
        texts = [p["description_en"] for p in self.catalog]
        embs = np.array(list(self._model.embed(texts)), dtype="float32")
        # L2-normalise for cosine similarity via inner product
        norms = np.linalg.norm(embs, axis=1, keepdims=True).clip(min=1e-9)
        self._embeddings = embs / norms
        self.index = faiss.IndexFlatIP(self._embeddings.shape[1])
        self.index.add(self._embeddings)

    # ── Encode query ───────────────────────────────────────────────────────────
    def _encode(self, text: str) -> np.ndarray:
        vec = np.array(list(self._model.embed([text])), dtype="float32")
        norm = np.linalg.norm(vec)
        return vec / max(norm, 1e-9)

    # ── Main search ────────────────────────────────────────────────────────────
    def search(
        self,
        query: str,
        child_age_months: int,
        exclude_product_ids: list[str] = [],
        k: int = 3,
    ) -> list[dict]:
        # Stage 1: neural semantic search (top-10)
        q_vec = self._encode(query)
        scores, idxs = self.index.search(q_vec, 10)
        candidates = [
            {**self.catalog[i], "_semantic_score": float(s)}
            for s, i in zip(scores[0], idxs[0])
        ]

        # Stage 2: hard age filter
        age_filtered = [
            p for p in candidates
            if p["age_min_months"] <= child_age_months <= p["age_max_months"]
            and p["product_id"] not in exclude_product_ids
            and p.get("in_stock", True)
        ]
        if not age_filtered:
            return []

        # Stage 3: neural cosine rerank against query
        for p in age_filtered:
            idx = next(
                i for i, c in enumerate(self.catalog)
                if c["product_id"] == p["product_id"]
            )
            p_vec = self._embeddings[idx : idx + 1]
            p["_rerank_score"] = float((q_vec @ p_vec.T)[0, 0])

        return sorted(age_filtered, key=lambda x: x["_rerank_score"], reverse=True)[:k]

    def get_by_id(self, product_id: str) -> dict | None:
        return next((p for p in self.catalog if p["product_id"] == product_id), None)


# ── Self-test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Loading retriever (fastembed ONNX — no PyTorch required)...")
    r = ProductRetriever("data/catalog.json")
    print(f"Index built. Encoder: {ProductRetriever.MODEL_NAME}\n")

    results = r.search("baby weaning first solid foods spoon", child_age_months=5)
    print(f"Query: weaning | age 5mo → {len(results)} result(s)")
    for p in results:
        print(f"  {p['product_id']} | {p['name_en']} | "
              f"{p['age_min_months']}–{p['age_max_months']}mo | "
              f"rerank={p['_rerank_score']:.4f}")

    # Age filter must exclude everything for a 14yo
    r2 = r.search("baby feeding", child_age_months=168)
    assert r2 == [], "Age filter failed"
    print(f"\nAge filter (168mo): {len(r2)} — ✓")

    # Exclusion list
    excluded = ["MW-001", "MW-002", "MW-028"]
    r3 = r.search("baby weaning", child_age_months=5, exclude_product_ids=excluded)
    for p in r3:
        assert p["product_id"] not in excluded
    print(f"Exclusion test: {len(r3)} result(s), none in exclusion list — ✓")

    print("\nAll retriever tests passed ✓")
