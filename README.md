# Regulation Q&A — Retrieval-Augmented Generation (RAG)

A document-grounded question-answering system that allows users to ask questions about regulatory PDF documents and receive answers with source citations.

Built using Python, FastAPI, FAISS, Sentence Transformers, and a locally hosted Phi-3 model through Ollama.

## 1. Project Overview

Regulatory documents are often lengthy and difficult to search manually. This project uses Retrieval-Augmented Generation (RAG) to retrieve relevant passages from regulatory PDFs and generate answers grounded in those passages.

**Key features**
- PDF text extraction with page-level metadata.
- Text chunking with overlapping segments.
- Semantic search using Sentence Transformers.
- Vector similarity search using FAISS.
- LLM-generated answers grounded in retrieved context.
- Source citations containing document names and page numbers.
- In-memory LRU caching for repeated questions.
- FastAPI endpoints for health checks and question answering.
- Evaluation using a custom dataset of 30 questions.
- Automated tests for ingestion, caching, and API functionality.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API framework | FastAPI |
| API server | Uvicorn |
| PDF extraction | pypdf |
| Embedding model | all-MiniLM-L6-v2 |
| Vector database/index | FAISS |
| LLM | Phi-3 Mini |
| Local model runtime | Ollama |
| LLM client | OpenAI-compatible AsyncOpenAI |
| Caching | Python OrderedDict (LRU) |
| Testing | pytest |
| Data format | JSON |

## 3. Architecture

```text
             Regulatory PDF Documents
                       |
                       v
                PDF Extraction
                       |
                       v
                 Text Chunking
                (500 characters,
                 100 overlap)
                       |
                       v
              Sentence Transformers
                 Embeddings
                       |
                       v
                  FAISS Index
                       |
                       v
              Persisted Storage
              (Index + Metadata)


                  USER QUERY
                       |
                       v
                  FastAPI API
                       |
                       v
                  Cache Check
                    /     \
                 HIT       MISS
                  |          |
                  |          v
                  |      FAISS Search
                  |          |
                  |          v
                  |     Top 3 Chunks
                  |          |
                  |          v
                  |     Grounded Prompt
                  |          |
                  |          v
                  |      Phi-3 Mini
                  |          |
                  |          v
                  |     Generated Answer
                  |          |
                  |          v
                  |       Cache Store
                  |          |
                  +----------+
                       |
                       v
               Answer + Citations
```

## 4. Project Structure

```text
regulation-rag/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion.py
│   ├── retrieval.py
│   ├── llm.py
│   ├── cache.py
│   └── main.py
│
├── data/
│   ├── pdfs/
│   └── evaluation_questions.json
│
├── storage/
│   ├── regulations.faiss
│   └── metadata.json
│
├── scripts/
│   ├── __init__.py
│   ├── ingest.py
│   ├── test_retrieval.py
│   ├── test_cache.py
│   ├── preview_documents.py
│   ├── check_page_coverage.py
│   ├── evaluate.py
│   └── benchmark_cache.py
│
├── tests/
│   ├── __init__.py
│   ├── test_ingestion.py
│   ├── test_cache.py
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Installation and Setup

### Prerequisites

- Python installed.
- Ollama installed.
- Git installed (for GitHub upload).

### Step 1: Clone the repository

```bash
git clone https://github.com/aakritisharma001/regulation-rag.git
cd regulation-rag
```

### Step 2: Create and activate a virtual environment

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Step 3: Install dependencies

```cmd
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file using `.env.example` as a reference.

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=phi3:mini

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TOP_K=3
```

### Step 5: Set up the local LLM

```cmd
ollama pull phi3:mini
```

Start the model:

```cmd
ollama run phi3:mini
```

Keep Ollama running while using the API.

### Step 6: Add regulatory PDFs

The regulatory PDF files are not included in this repository. Add your own permitted PDF documents to this folder before running ingestion. The data/pdfs/ directory is excluded from Git.
Place your PDF documents inside:

```text
data/pdfs/
```

### Step 7: Run document ingestion

```cmd
python -m scripts.ingest
```

This extracts text, creates chunks, generates embeddings, and saves the FAISS index and metadata.

### Step 8: Start the API

```cmd
uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 6. API Endpoints

### GET /health

Checks whether the API is running.

### POST /ask

Accepts a question and returns an answer with source information.

Example request:

```json
{
  "question": "What is the Reserve Bank of India?"
}
```

Example response structure:

```json
{
  "question": "What is the Reserve Bank of India?",
  "answer": "Generated answer with source citation [Source 1]",
  "sources": [
    {
      "source": 1,
      "document": "example.pdf",
      "page": 1,
      "similarity": 0.85
    }
  ],
  "cache": "MISS"
}
```

The actual answer and source details depend on the documents and question.

## 7. Evaluation

A custom evaluation dataset of 30 questions was created across six regulatory PDF documents.

Retrieval performance was measured using Hit Rate@3 and Hit Rate@5.

### Retrieval Evaluation Results

| Metric | Result |
|---|---:|
| Evaluation questions | 30 |
| Hit Rate@3 | 100% |
| Hit Rate@5 | 100% |
| Average retrieval time | 17.31 ms |

### Cache Benchmark Results

The cache was benchmarked using five questions, each submitted twice.

| Metric | Average latency |
|---|---:|
| Cache MISS | 33,869.66 ms |
| Cache HIT | 5.37 ms |
| Approximate speedup | 6,305.20x |

The first request required retrieval and LLM generation. Repeated requests returned the cached response.

**Note:** These are local benchmark results from a five-question cache test and a 30-question retrieval evaluation. Results may vary depending on hardware, model loading, and system conditions.

## 8. Running Tests

Execute:

```cmd
pytest -v
```

The test suite covers:
- Text chunking and input validation.
- Cache storage and LRU eviction.
- API health endpoint.
- Question-answering endpoint.
- Cache-hit behaviour.

## 9. Design Considerations

- **Grounded generation:** The LLM is instructed to answer using retrieved document context rather than relying on outside knowledge.
- **Source traceability:** Retrieved passages retain document names and page numbers.
- **Efficient retrieval:** FAISS enables similarity search over stored embeddings.
- **Caching:** Repeated questions can avoid expensive LLM generation.
- **Configuration:** Model settings are managed through environment variables.
- **Modularity:** Ingestion, retrieval, caching, and API logic are separated into individual modules.

## 10. Future Improvements

- Add more regulatory documents and expand the evaluation dataset.
- Improve retrieval using reranking and hybrid search.
- Add more robust document-level and answer-level evaluation.
- Introduce Redis for shared, persistent caching.
- Add authentication and rate limiting.
- Improve PDF extraction for scanned documents using OCR.
- Add containerisation and deployment support.

---

**Project:** Regulation Q&A — RAG-based Regulatory Document Assistant  
**Focus:** AI Engineering | Retrieval-Augmented Generation | Backend Development