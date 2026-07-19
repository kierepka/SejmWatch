# SejmWatch

SejmWatch turns complex Polish legislative documents into a verified timeline of changes, personalized impact alerts, and answers backed by page-level citations.

The hackathon MVP follows one complete path: two versions of one legislative document are imported page by page, linked to the same case, compared deterministically at article level, and made searchable. GPT‑5.6 may synthesize an answer, but the application accepts it only when every citation points to an existing page and the quoted text actually occurs on that page.

## Run the demo

### Docker (recommended for judges)

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000). The public synthetic demo dataset loads automatically and does not require an API key. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` to enable GPT‑5.6 answers.

The **Najnowsze druki** screen reads live metadata from the official
[Sejm API](https://api.sejm.gov.pl/sejm.html). Import downloads the first PDF
attachment from the same official API, extracts it page by page, and links
prints through their `processPrint` identifier.

### Local Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn sejmwatch.app:app --reload
```

Run tests with `pytest`.

## Demo path

1. Open **Odporność cyfrowa ochrony zdrowia**.
2. Review the deterministic comparison of the original and committee versions.
3. Notice that Article 14 changes the transition period from 24 to 12 months and Article 15 is new.
4. Ask: “Jak zmienił się okres dostosowawczy?”
5. Inspect the page-level quote and official-document link.
6. In the tests, see invalid pages and invented quotes rejected.

The bundled data is intentionally synthetic and clearly labelled `druk-demo-*`; its source links lead to the official Sejm print index. This keeps the demo stable and redistributable. Production imports use official HTTPS PDF URLs through `sejmwatch.ingest.download_pdf()` and retain one text record per PDF page.

## Architecture

```mermaid
flowchart LR
  A[Official PDF] --> B[PyMuPDF page extraction]
  B --> C[SQLite + FTS5]
  C --> D[Deterministic article diff]
  D --> E[GPT-5.6 structured answer]
  E --> F[Quote and page validator]
  F --> G[Timeline and evidence-first Q&A]
```

No vector database is required for the MVP. FTS5 provides explainable lexical retrieval, while document and case metadata prevent unrelated legislative matters from being mixed.

## Evidence contract

Generated answers use a typed structure containing `answer`, `confidence`, and at least one evidence object with `document_id`, `page`, `quote`, and source URL. `validate_evidence()` rejects output when:

- there is no citation;
- the document or page does not exist;
- the quote cannot be found on that page;
- two compared documents belong to different cases.

This is an informational tool, not legal advice. The UI always exposes the underlying quote and source document.

## What was built during the hackathon

- PDF download and page-preserving extraction;
- SHA-256 document identity and version linkage;
- article-aware deterministic diff;
- SQLite/FTS5 retrieval scoped to a legislative case;
- GPT‑5.6 Responses API integration with Pydantic structured output;
- post-generation evidence validation;
- server-rendered timeline and Q&A interface;
- stable demo data, Docker setup, and core tests.

Nothing in this repository predates the hackathon scaffold. Future work—continuous Sejm monitoring, OCR, alerts, Senate/RCL sources, voting links, multi-user profiles, and Bielik/Ollama—is explicitly outside this MVP.

## Codex and human collaboration

Codex was used as the implementation partner for repository scaffolding, architecture translation, application code, tests, container setup, and documentation. GPT‑5.6 is used at runtime only for grounded synthesis through the OpenAI Responses API; retrieval, version comparison, and evidence validation remain deterministic.

The human chose the product scope, the Health & MedTech demonstration profile, the evidence-first safety policy, and the final submission narrative. Before submission, add the Codex Session ID obtained with `/feedback` and preserve the repository commit history from the contest period.

## API entry points

- `GET /` — monitored legislative cases
- `GET /cases/{case_id}` — version history and changes
- `POST /cases/{case_id}/ask` — grounded Q&A
- `GET /health` — container health check
- `GET /sejm` — latest official Sejm prints
- `POST /sejm/import/{number}` — import the official PDF for a print

The lower-level import and comparison functions are in `sejmwatch/ingest.py` and `sejmwatch/diffing.py` for use by a future monitoring worker.

## Lowest-cost Heroku profile

The application needs one web dyno and no paid add-ons, worker, scheduler, or
managed database. SQLite lives on Heroku's ephemeral filesystem, so imported
official documents can disappear after a restart or dyno replacement; the
bundled demo is recreated automatically. This is the intentional low-cost
hackathon trade-off. Add Postgres or object storage only when persistent
monitoring becomes a requirement.
