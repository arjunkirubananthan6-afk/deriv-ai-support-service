# AI Support Answer Service

## Overview

This project implements a lightweight AI-style customer support answering service using Python. It retrieves relevant information from a local knowledge base and determines whether there is sufficient evidence to answer a user's question.

The system follows four stages:

**LOAD_KB → RETRIEVE → CHECK_SUPPORT → ANSWER / ABSTAIN**

The main objective is to provide answers grounded in the knowledge base rather than generate unsupported information.

## Project Structure

```text
DERIV/
├── app.py
├── retriever.py
├── support.py
├── kb.json
├── test_app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.11 or newer
- scikit-learn
- pytest (for testing)

## Installation

Open a terminal in the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Application

The application provides a command-line interface.

Run:

```powershell
python app.py "How long does a password reset link last?"
```

The application prints a JSON response with the following fields:

- `question`: The original question.
- `decision`: Either `answer` or `abstain`.
- `answer`: A sentence from the knowledge base or a fallback response.
- `citations`: Supporting document IDs, titles, and snippets.
- `debug`: Retrieved document IDs and a support score.

## System Design

### 1. LOAD_KB

The `KnowledgeBaseRetriever` class loads the knowledge base from `kb.json`.

Each knowledge-base document must contain three string fields:

- `id`
- `title`
- `text`

The knowledge base is loaded dynamically, allowing the application to work with replacement documents that follow the same format.

### 2. RETRIEVE

The application uses TF-IDF vectorization with unigram and bigram features to represent knowledge-base documents.

Cosine similarity is used to compare the user's question with the documents.

The three highest-ranked documents with positive similarity scores are returned.

### 3. CHECK_SUPPORT

The application evaluates whether retrieved information sufficiently supports the question.

The evidence-checking process includes:

- A minimum retrieval similarity threshold.
- Keyword coverage across the document.
- Keyword coverage across supporting sentences.
- Explicit numerical time evidence for duration questions.
- Restrictions on guarantees and certain legal or tax advice requests.
- Additional lexical checks to reduce mismatches between subjects.

If no evidence satisfies these conditions, the system abstains.

The support score is a heuristic derived from evidence coverage. It is not a calibrated probability.

### 4. ANSWER / ABSTAIN

If sufficient evidence is identified, the system returns a supporting sentence directly from the knowledge base.

The response includes a citation containing the document ID, title, and supporting snippet.

If evidence is insufficient, the system returns:

"I don't have enough information in the knowledge base to answer that question. Please contact human support."

Abstention responses contain an empty citations list.

## Testing

Automated tests are implemented using pytest.

Run:

```powershell
python -m pytest -q
```

The test suite covers:

- Answerable support questions.
- Questions requiring abstention.
- JSON response structure.
- Loading and querying a replacement knowledge base.

## Design Decisions

**TF-IDF retrieval:** Chosen because it is lightweight, deterministic, and does not require external API access.

**Extractive answering:** Supporting sentences are returned directly from the knowledge base to avoid generating new unsupported claims.

**Conservative abstention:** The system attempts to reject questions when evidence is insufficient.

**Modular architecture:** Retrieval, support checking, and application execution are separated into independent Python files.

## Limitations

The system relies primarily on keyword overlap rather than full semantic understanding.

It may fail to recognize valid paraphrases or may incorrectly associate related terms with unsupported actions. For example, mentioning an email address in a password-reset article does not necessarily establish whether support agents can change a user's email address.

The system therefore does not guarantee perfect factual support detection. More advanced semantic entailment checking could improve reliability.

The application runs locally and does not require an external language model or API key.