import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class JsonSearchEngine:
    def __init__(self, data: Path, source: str):
        self.data = json.loads(data)[source]
        self.documents = []
        self.metadata = []

    def document(self):
        for category, items in self.data.items():
            for item in items:
                text = f"{item['title']} {item['content']}"
                self.documents.append(text)
                self.metadata.append({**item, "category": category})

    def vectorize(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query, top_k=5):
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            results.append({
                **self.metadata[idx],
                "score": float(scores[idx])
            })

        return results