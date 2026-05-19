# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
import json
from itertools import islice
from pathlib import Path


class SearchEngine:
    def __init__(self, sources: str, query: str, max_results: int):
        self.sources = sources
        self.query = query
        self.max_results = max_results

    def _read(self, data: Path) -> list[dict[str, str]]:
        with open(data) as f:
            data = json.load(f)

        return data[self.sources]

    def _search(self, data: list[dict[str, str]]) -> list[dict[str, str]]:
        results = list(
            islice(
                (
                    item
                    for item in data
                    if self.query.lower() in item["title"].lower()
                    or self.query.lower() in item["description"].lower()
                ),
                self.max_results,
            )
        )
        return results

    def run(self, data: Path) -> list[dict[str, str]]:
        data = self._read(data)
        return self._search(data)

    # def __init__(self, data):
    #     self.data = data
    #     self.documents = []
    #     self.metadata = []

    # def document(self):
    #     for category, items in self.data.items():
    #         for item in items:
    #             text = f"{item['title']} {item['content']}"
    #             self.documents.append(text)
    #             self.metadata.append({**item, "category": category})

    # def vectorize(self):
    #     self.vectorizer = TfidfVectorizer(stop_words="english")
    #     self.matrix = self.vectorizer.fit_transform(self.documents)

    # def search(self, query, top_k=5):
    #     query_vec = self.vectorizer.transform([query])
    #     scores = cosine_similarity(query_vec, self.matrix).flatten()

    #     ranked_indices = scores.argsort()[::-1][:top_k]

    #     results = []
    #     for idx in ranked_indices:
    #         results.append({**self.metadata[idx], "score": float(scores[idx])})

    #     return results
