# SejmWatch — OpenAI Build Week submission package

## Recommended track

**Work & Productivity**

SejmWatch reduces the time required by public-interest teams, journalists,
small businesses, NGOs, and policy professionals to understand how a Polish
bill changes between official versions.

## Project name

SejmWatch

## Tagline

Evidence-first AI for tracking how Polish legislation changes—and what those
changes mean.

## Short pitch

SejmWatch turns official Polish parliamentary documents into a verifiable
timeline of legislative changes. It downloads source PDFs, preserves page
numbers, compares versions at article level, and answers questions only when
the cited quotation can be found on the stated page.

## Full Devpost description

### Inspiration

Important legislative changes are often spread across long PDFs, committee
reports, and successive parliamentary prints. Citizens and professionals must
manually locate the current version, compare it with earlier documents, and
work out who is responsible for the process. A fluent AI summary without
evidence does not solve that trust problem.

SejmWatch was built to make legislative change understandable without
separating an answer from its official source.

### What it does

SejmWatch reads live metadata from the official Sejm API and imports official
parliamentary PDFs page by page. Documents belonging to the same legislative
case are linked and compared deterministically at article level.

The public demonstration follows the Polish government bill on artificial
intelligence systems through official prints 2443 and 2614. Users can:

- inspect detected additions, removals, and modifications;
- explore the process as a keyboard-accessible 3D change tree;
- see the responsible committee, chair, and rapporteur where official data is
  available;
- ask questions through retrieval-augmented generation;
- generate a thematic report for topics such as AI in medicine or hospital
  cybersecurity;
- inspect the exact quotation, page number, and official PDF behind an answer;
- use the interface in Polish or English while official legal text remains in
  its source language.

The evidence validator rejects an AI answer when it has no citation, points to
a page that does not exist, or contains a quotation that cannot be found on
that page.

### How we built it

- FastAPI and Jinja2 provide a lightweight server-rendered application.
- The official Sejm API supplies prints, processes, interpellations,
  committees, and member data.
- PyMuPDF extracts official PDFs while preserving page boundaries.
- SQLite and FTS5 provide explainable lexical retrieval.
- A deterministic article-aware diff identifies textual changes.
- Pydantic defines the answer and evidence contract.
- An OpenAI-compatible model performs grounded synthesis; deterministic code
  independently validates its evidence.
- A single web process checks recent print metadata every six hours without a
  separate scheduler or managed database.
- Docker Compose and pytest provide a reproducible local path.

### Evidence-first design

The model is not the source of truth. Retrieval, case scoping, document
version linkage, article comparison, and quote validation are deterministic.
The model explains retrieved material, while the application verifies that
the evidence exists before displaying the answer.

This separation is especially important for legal and public-interest
information.

### How Codex was used

Codex served as the implementation partner throughout the build. It translated
the initial public-interest concept into the data model and vertical slice,
implemented official API integration and PDF ingestion, added deterministic
diffing and evidence validation, removed mock data, built the report generator
and accessible 3D tree, added the bilingual interface, wrote tests, deployed
the application, and repeatedly checked the live result.

The human made the product decisions: choosing the Health & MedTech scenario,
requiring official sources, refusing invented attribution of amendments,
prioritising a no-add-on deployment, and keeping official legal text
untranslated unless an official translation exists.

### GPT-5.6 usage — complete before submission

Replace this section only after a real GPT-5.6 run has been performed and
saved in the repository or demo. State exactly which project task GPT-5.6
performed, what input it received, and how the deterministic validator checked
its result. Do not claim that the public runtime uses GPT-5.6 while it is
configured with another model.

### Challenges

The central challenge was preventing a fluent answer from outrunning its
evidence. Page identity must survive extraction, retrieval, generation, and
display. We store one record per PDF page and treat citations as typed data
that is validated after generation.

Another challenge was attribution. Official metadata can identify a committee
or rapporteur, but does not attribute every textual difference to a particular
MP. SejmWatch presents the available responsibility data and explicitly
refuses to guess authorship.

### Accomplishments

- Real official documents instead of mock legislative data.
- Page-preserving PDF ingestion and SHA-256 identity.
- Deterministic article-level comparisons.
- Case-scoped RAG with exact-quote validation.
- A reusable thematic report generator.
- Keyboard-accessible simple and full 3D navigation.
- Polish and English UI with source-language safeguards.
- Live Sejm metadata monitoring without paid add-ons.
- A public working deployment and automated core tests.

### What we learned

Reliable public-interest AI needs a clear boundary between probabilistic
explanation and deterministic verification. Keeping provenance at page level
makes answers more trustworthy and makes failures visible instead of hiding
them behind confident prose.

### What's next

Next steps are persistent storage, automatic import of selected new PDFs,
topic subscriptions, outbound alerts, OCR for scanned documents, Senate and
Government Legislation Centre sources, voting links, and structured amendment
authorship where official data supports it.

## Built with

Codex, GPT-5.6 (only after verified use), Python, FastAPI, Jinja2, SQLite,
FTS5, PyMuPDF, Pydantic, pytest, Docker, Heroku, Sejm API, Cerebras,
gpt-oss-120b

## Public links

- Live demo: https://sejmwatch-c0e8a67cd6b2.herokuapp.com/
- English demo: https://sejmwatch-c0e8a67cd6b2.herokuapp.com/en
- 3D change tree:
  https://sejmwatch-c0e8a67cd6b2.herokuapp.com/cases/sejm-10-2443/tree
- Report generator:
  https://sejmwatch-c0e8a67cd6b2.herokuapp.com/reports/new
- Repository: https://github.com/kierepka/SejmWatch

## Required Devpost answers

- **Submitter Type (27945):** Individual — confirm before final submission.
- **Country (27946):** Poland — confirm before final submission.
- **Category (27947):** Work & Productivity.
- **Repository (27948):** https://github.com/kierepka/SejmWatch
- **Testing instructions (27949):** Open the live demo. Select the AI systems
  bill, inspect the deterministic change list or 3D tree, and ask a question.
  Each accepted answer shows an exact quotation, page, and official PDF. No
  credentials are required. Use `/en` for the English interface.
- **Codex Session ID (27950):** obtain using `/feedback` in the primary Codex
  build thread.
- **Developer-tool instructions (27951):** Not applicable.

## Do not submit until

1. A real, meaningful GPT-5.6 use is visible in code/history and the video.
2. The `/feedback` Session ID has been obtained.
3. A public YouTube video shorter than three minutes has been added.
4. Submitter type and country have been confirmed.
5. The final Devpost preview contains the current official-data description,
   not the old synthetic-demo description.
