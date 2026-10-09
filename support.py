
import re

FALLBACK = (
    "I don't have enough information in the knowledge base "
    "to answer that question. Please contact human support."
)

MIN_RETRIEVAL_SCORE = 0.12
MIN_DOCUMENT_COVERAGE = 0.60
MIN_SENTENCE_SCORE = 0.35

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be",
    "to", "from", "for", "of", "in", "on", "at", "by",
    "and", "or", "do", "does", "did", "can", "could",
    "i", "my", "me", "you", "your", "how", "what",
    "when", "where", "why", "who", "will", "would",
    "please", "tell", "about", "it", "this", "that",
    "there", "any"
}

RESTRICTED_TERMS = {
    "guarantee", "guaranteed", "promise", "promised",
    "legal advice", "tax advice"
}

DURATION_QUESTIONS = (
    "how long",
    "how many minutes",
    "how many hours",
    "how many days",
    "duration",
    "length of time"
)

DURATION_PATTERN = (
    r"\b\d+\s*"
    r"(?:minutes?|hours?|days?|weeks?|months?|years?)\b"
)



def normalize(word):
    # Normalize common grammatical variations
    if word in ("close", "closed", "closing", "closure"):
        return "close"

    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and len(word) > 4:
        return word[:-1]

    return word


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {
        normalize(word)
        for word in words
        if word not in STOP_WORDS
    }


def split_sentences(text):
    return re.split(r"(?<=[.!?])\s+", text.strip())


def is_duration_question(question):
    question_lower = question.lower()
    return any(
        phrase in question_lower
        for phrase in DURATION_QUESTIONS
    )


def has_duration(sentence):
    return bool(
        re.search(DURATION_PATTERN, sentence.lower())
    )


def is_restricted(question):
    question_lower = question.lower()

    if any(term in question_lower for term in RESTRICTED_TERMS):
        return True

    # Reject requests for exact bounds unless explicitly supported
    if is_duration_question(question):
        if any(
            term in question_lower
            for term in (
                "shortest", "minimum", "maximum",
                "exactly", "definitely", "certain"
            )
        ):
            return True

    return False


def subject_words(question):
    words = tokenize(question)

    if is_duration_question(question):
        duration_terms = {
            "long", "length", "time", "duration",
            "minute", "hour", "day", "week",
            "month", "year", "short", "shortest"
        }
        words -= duration_terms

    return words


def coverage_score(question_words, evidence_words):
    if not question_words:
        return 0.0

    return len(question_words & evidence_words) / len(question_words)



def subject_conflict(question, document):
    question_lower = question.lower()
    document_lower = document.lower()

    # Distinguish different address types
    address_types = (
        "email address",
        "residential address",
        "postal address",
        "billing address"
    )

    mentioned = [
        phrase for phrase in address_types
        if phrase in question_lower
    ]

    if mentioned:
        return not any(
            phrase in document_lower
            for phrase in mentioned
        )

    return False


def check_support(question, retrieved):
    if not retrieved:
        return None, 0.0

    top_score = retrieved[0]["score"]

    if top_score < MIN_RETRIEVAL_SCORE:
        return None, 0.0

    if is_restricted(question):
        return None, 0.0

    question_words = subject_words(question)

    if not question_words:
        return None, 0.0

    candidates = []
    duration_question = is_duration_question(question)

    for doc in retrieved:
        if doc["score"] < MIN_RETRIEVAL_SCORE:
            continue

        if subject_conflict(
            question,
            doc["title"] + " " + doc["text"]
        ):
            continue

        document_words = tokenize(
            doc["title"] + " " + doc["text"]
        )

        document_coverage = coverage_score(
            question_words, document_words
        )

        if document_coverage < MIN_DOCUMENT_COVERAGE:
            continue

        for sentence in split_sentences(doc["text"]):
            sentence_words = tokenize(sentence)

            # Include the document title for context
            evidence_words = sentence_words | tokenize(doc["title"])

            sentence_coverage = coverage_score(
                question_words, evidence_words
            )

            if sentence_coverage < MIN_SENTENCE_SCORE:
                continue

            # Duration questions require actual duration evidence
            if duration_question and not has_duration(sentence):
                continue

            # Prefer evidence that directly matches the question
            score = (
                0.7 * sentence_coverage
                + 0.3 * document_coverage
            )

            candidates.append({
                "sentence": sentence,
                "score": round(score, 4),
                "document": doc
            })

    if not candidates:
        return None, 0.0

    best = max(
        candidates,
        key=lambda item: (
            item["score"],
            item["document"]["score"]
        )
    )

    return best, best["score"]
