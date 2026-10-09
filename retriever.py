import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBaseRetriever:
    def __init__(self, kb_path="kb.json"):
        # Load the knowledge base from disk
        path = Path(kb_path)
        with path.open("r", encoding="utf-8") as file:
            self.documents = json.load(file)

        # Validate the knowledge base structure
        if not isinstance(self.documents, list):
            raise ValueError("Knowledge base must be a JSON array.")

        for doc in self.documents:
            if not isinstance(doc, dict) or not all(
                isinstance(doc.get(key), str) and doc[key].strip()
                for key in ("id", "title", "text")
            ):
                raise ValueError("Each document must contain id, title and text.")

        # Prepare TF-IDF retrieval
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        self.matrix = None

        if self.documents:
            passages = [
                doc["title"] + " " + doc["text"]
                for doc in self.documents
            ]
            self.matrix = self.vectorizer.fit_transform(passages)

    def retrieve(self, question, top_k=3):
        if self.matrix is None or not question.strip():
            return []

        # Convert the question into a TF-IDF vector
        question_vector = self.vectorizer.transform([question])

        # Compare the question with each document
        scores = cosine_similarity(
            question_vector, self.matrix
        )[0]

        # Sort by relevance, highest first
        ranked_indices = scores.argsort()[::-1]

        results = []

        for index in ranked_indices[:top_k]:
            score = float(scores[index])

            if score <= 0:
                continue

            doc = self.documents[index]

            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc["text"],
                "score": round(score, 4)
            })

        return results
