
import json

import pytest

from app import ask
from retriever import KnowledgeBaseRetriever


@pytest.fixture
def retriever():
    return KnowledgeBaseRetriever("kb.json")


@pytest.mark.parametrize("question,expected_id", [
    ("How long does a password reset link last?", "doc_1"),
    ("How do I enable two-factor authentication?", "doc_2"),
    ("How long does withdrawal review take?", "doc_3"),
    ("How do I close my account?", "doc_4"),
    ("How can I update my residential address?", "doc_5"),
])
def test_answerable_questions(retriever, question, expected_id):
    result = ask(question, retriever)

    assert result["decision"] == "answer"
    assert result["citations"]
    assert result["citations"][0]["id"] == expected_id
    assert result["answer"] == result["citations"][0]["snippet"]


@pytest.mark.parametrize("question", [
    "Can you guarantee my withdrawal will finish in 2 hours?",
    "What tax advice do you provide for closed accounts?",
    "What is the weather tomorrow?",
    "How long does account closure take?",
])
def test_unanswerable_questions(retriever, question):
    result = ask(question, retriever)

    assert result["decision"] == "abstain"
    assert result["citations"] == []
    assert "contact human support" in result["answer"].lower()


def test_replacement_knowledge_base(tmp_path):
    replacement = [
        {
            "id": "new_1",
            "title": "Delivery tracking",
            "text": "Customers can track deliveries from the Orders page."
        }
    ]

    path = tmp_path / "kb.json"
    path.write_text(json.dumps(replacement), encoding="utf-8")

    custom_retriever = KnowledgeBaseRetriever(str(path))

    result = ask(
        "How can customers track deliveries?",
        custom_retriever
    )

    assert result["decision"] == "answer"
    assert result["citations"][0]["id"] == "new_1"


def test_json_schema(retriever):
    result = ask("How do I enable two-factor authentication?", retriever)

    assert set(result) == {
        "question", "decision", "answer", "citations", "debug"
    }
    assert isinstance(result["debug"]["retrieved_ids"], list)
    assert isinstance(result["debug"]["support_score"], (int, float))
