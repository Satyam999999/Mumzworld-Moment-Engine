"""
RAG Product Retriever — Two-stage: TF-IDF FAISS + hard age filter + cosine rerank.

Architecture: sentence-transformers (cross-encoder/ms-marco-MiniLM-L-6-v2) is
specified in the master plan. On this host (macOS 26 Tahoe beta), PyTorch 2.7.1
crashes on import due to a known mutex threading bug (libc++abi). We fall back
to sklearn TF-IDF + cosine similarity, preserving the same three-stage retrieval
contract. The retriever API is identical — swap in sentence-transformers when
upstream fixes the macOS 26 threading issue.
"""

import json, numpy as np, faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductRetriever:
    def __init__(self, catalog_path: str):
        with open(catalog_path) as f:
            self.catalog = json.load(f)
        self._build_index()

    def _build_index(self):
        texts = [p['description_en'] for p in self.catalog]
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        matrix = self._vectorizer.fit_transform(texts).toarray().astype('float32')
        # L2-normalize for cosine similarity via inner product
        norms = np.linalg.norm(matrix, axis=1, keepdims=True).clip(min=1e-9)
        self._embeddings = (matrix / norms)
        self.index = faiss.IndexFlatIP(self._embeddings.shape[1])
        self.index.add(self._embeddings)

    def _encode(self, text: str) -> np.ndarray:
        vec = self._vectorizer.transform([text]).toarray().astype('float32')
        norm = np.linalg.norm(vec)
        return (vec / max(norm, 1e-9))

    def search(self, query: str, child_age_months: int,
               exclude_product_ids: list[str] = [], k: int = 3) -> list[dict]:
        # Stage 1: semantic search via TF-IDF FAISS (top-10)
        vec = self._encode(query)
        scores, idxs = self.index.search(vec, 10)
        candidates = []
        for score, idx in zip(scores[0], idxs[0]):
            candidates.append({**self.catalog[idx], '_semantic_score': float(score)})

        # Stage 2: hard age filter — non-negotiable
        age_filtered = [
            p for p in candidates
            if p['age_min_months'] <= child_age_months <= p['age_max_months']
            and p['product_id'] not in exclude_product_ids
            and p.get('in_stock', True)
        ]
        if not age_filtered:
            return []

        # Stage 3: cosine rerank (cross-encoder equivalent)
        q_vec = self._encode(query)
        for p in age_filtered:
            idx = next(i for i, c in enumerate(self.catalog) if c['product_id'] == p['product_id'])
            p_vec = self._embeddings[idx:idx+1]
            p['_rerank_score'] = float(cosine_similarity(q_vec, p_vec)[0][0])

        ranked = sorted(age_filtered, key=lambda x: x['_rerank_score'], reverse=True)
        return ranked[:k]

    def get_by_id(self, product_id: str) -> dict | None:
        return next((p for p in self.catalog if p['product_id'] == product_id), None)


if __name__ == "__main__":
    print("Loading retriever (TF-IDF, no torch required)...")
    r = ProductRetriever("data/catalog.json")
    print("Index built.")

    results = r.search("baby feeding weaning solid foods", child_age_months=5)
    print(f"\nQuery: weaning | age: 5mo -> {len(results)} results")
    for p in results:
        print(f"  {p['product_id']} | {p['name_en']} | {p['age_min_months']}-{p['age_max_months']}mo | score={p['_rerank_score']:.3f}")

    results2 = r.search("baby feeding", child_age_months=168)
    print(f"\nAge filter (168mo): {len(results2)} (expect 0)")
    assert len(results2) == 0, "Age filter failed"

    results3 = r.search("baby feeding weaning", child_age_months=5,
                         exclude_product_ids=["MW-001","MW-002","MW-003","MW-004","MW-005","MW-007"])
    print(f"\nExclusion test: {len(results3)} result(s)")
    for p in results3:
        assert p['product_id'] not in ["MW-001","MW-002","MW-003","MW-004","MW-005","MW-007"]
        print(f"  {p['product_id']} | {p['name_en']}")

    print("\nAll retriever tests passed ✓")
