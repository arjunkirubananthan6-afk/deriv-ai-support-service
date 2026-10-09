import json
import sys

from retriever import KnowledgeBaseRetriever
from support import check_support, FALLBACK


def ask(question, retriever):
    # Stage 1 and 2: Retrieve relevant documents
    retrieved = retriever.retrieve(question)

    # Stage 3: Check whether sufficient evidence exists
    evidence, support_score = check_support(question, retrieved)

    # Stage 4: Abstain if evidence is insufficient
    if evidence is None:
        return {
            "question": question,
            "decision": "abstain",
            "answer": FALLBACK,
            "citations": [],
            "debug": {
                "retrieved_ids": [doc["id"] for doc in retrieved],
                "support_score": support_score
            }
        }

    # Stage 4: Answer using the supporting sentence
    doc = evidence["document"]
    sentence = evidence["sentence"]

    return {
        "question": question,
        "decision": "answer",
        "answer": sentence,
        "citations": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "snippet": sentence
            }
        ],
        "debug": {
            "retrieved_ids": [doc["id"] for doc in retrieved],
            "support_score": support_score
        }
    }


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python app.py \"your question\"",
            file=sys.stderr
        )
        sys.exit(1)

    question = " ".join(sys.argv[1:]).strip()

    retriever = KnowledgeBaseRetriever()
    result = ask(question, retriever)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
