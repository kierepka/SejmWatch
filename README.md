# SejmWatch

SejmWatch turns complex Polish legislative documents into a verified timeline
of changes, thematic reports, and answers backed by page-level citations.

**Live demo:** https://sejmwatch-c0e8a67cd6b2.herokuapp.com/

**English UI:** https://sejmwatch-c0e8a67cd6b2.herokuapp.com/en

The application imports official legislative documents page by page, links
versions to the same case, compares them deterministically at article level,
and makes them searchable. Public questions use a free-tier AI provider with
retrieved source pages attached to the response.

## Run the application

### Docker

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000). On first start the
application downloads official prints 2443 and 2614, extracts their real PDF
pages, and computes their article-level comparison. No fabricated legislative
records are loaded.

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

## Verification path

1. Open **Rządowy projekt ustawy o systemach sztucznej inteligencji**.
2. Review the comparison of official prints 2443 and 2614.
3. Inspect detected changes against the linked official PDFs.
4. Ask about responsibilities or the legislative changes.
5. Inspect the page-level quote and official-document link.
6. In the tests, see invalid pages and invented quotes rejected.

Every application record originates from an official HTTPS PDF URL through
`sejmwatch.ingest.download_pdf()` and retains one text record per PDF page.

## Architecture

```mermaid
flowchart LR
  A[Official PDF] --> B[PyMuPDF page extraction]
  B --> C[SQLite + FTS5]
  C --> D[Deterministic article diff]
  D --> E[Free-tier AI synthesis]
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
- OpenAI-compatible free-tier AI integration;
- post-generation evidence validation;
- server-rendered timeline and Q&A interface;
- official Sejm synchronization, Docker setup, and core tests.

The single web process also checks a recent snapshot of Sejm print metadata at
startup and every six hours. This deliberately avoids a separate scheduler or
worker. OCR, outbound alerts, Senate/RCL sources, voting links, multi-user
profiles, and Bielik/Ollama remain future work.

## Codex and human collaboration

Codex was used as the implementation partner for repository scaffolding,
architecture translation, application code, tests, container setup, and
documentation. Retrieval, version comparison, and evidence validation remain
deterministic; the language model only synthesizes an answer from retrieved
context.

The human chose the product scope, the Health & MedTech profile, the
evidence-first safety policy, and the final submission narrative.

GPT-5.6 was used through Codex as the reasoning model during project creation.
It contributed to architecture, implementation, official API integration,
evidence validation, tests, debugging, accessible interaction, bilingual UI,
deployment, and live verification. The human retained the product decisions
around scope, source integrity, attribution, and cost.

The public deployment separately uses the free-tier Cerebras-compatible
endpoint with `gpt-oss-120b`. GPT-5.6 was the build-time model in Codex; it is
not misrepresented as the public runtime model.

## Submission materials

- [Devpost submission package](SUBMISSION.md)
- [Demo video script](DEMO_SCRIPT.md)
- [Final submission checklist](SUBMISSION_CHECKLIST.md)

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
official documents can disappear after a restart or dyno replacement. The
canonical AI case is then reconstructed from official Sejm PDFs. Add Postgres
or object storage only when persistent monitoring becomes a requirement.
The monitor therefore reconstructs its baseline after a dyno replacement.

## License

MIT
