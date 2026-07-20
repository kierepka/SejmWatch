# SejmWatch — Codex and GPT-5.6 build log

## Provenance statement

SejmWatch was created entirely through Codex sessions using GPT-5.6. There was
no separately developed application or pre-existing implementation outside
this workflow. The Git history records the resulting implementation stages.

Codex was used not only to generate code, but to inspect official APIs, reason
about product scope, implement and revise the architecture, test locally,
operate the browser for interaction checks, deploy to GitHub and Heroku,
verify production behavior, audit claims against the implementation, and
prepare the competition submission.

The human remained responsible for the product direction and approvals. The
human selected the civic-use case, required a zero-add-on deployment, rejected
mock legislative records, requested the Health & MedTech example, required
responsibility information and official sources, chose the 3D tree direction,
requested keyboard navigation and an English UI, and required that legal text
not be unofficially translated.

## Chronological build summary

### 1. Product scope and evidence-first MVP

Commit: `4ab2c97` — **Build evidence-first SejmWatch MVP**

Codex translated the initial SejmWatch concept into a working FastAPI
application with:

- a SQLite data model for cases, documents, pages, and changes;
- page-preserving PDF ingestion with PyMuPDF;
- SHA-256 document identity;
- FTS5 retrieval;
- article-aware deterministic diffing;
- typed Pydantic evidence objects;
- a quote and page validator;
- server-rendered views, Docker configuration, and core tests.

The key joint decision was to separate probabilistic explanation from
deterministic evidence verification.

### 2. Deployable Python application

Commit: `29f1351` — **Add Heroku Python dependency manifest**

Codex prepared the Python dependency manifest and deployment entry points so
the same application could run locally, in Docker, and on Heroku.

### 3. Public AI question answering

Commit: `6cb143d` — **Add free AI question answering**

Codex added an OpenAI-compatible question-answering path, source retrieval,
rate limiting, and user-facing response views. The human required that the
public model path avoid additional charges.

### 4. Removal of mocks and switch to official records

Commits:

- `9a37aad` — **Replace sample data with official Sejm documents**
- `674286a` — **Remove legacy sample and OpenAI paths**

After the human rejected mock data, Codex removed the synthetic demonstration
and connected the application to official Sejm data and PDFs. The canonical
case now uses official prints 2443 and 2614 from the AI systems legislative
process.

### 5. Legislative accountability and 3D exploration

Commit: `db666cc` — **Add interactive 3D change tree and accountability**

Codex implemented the interactive change tree and official responsibility
panel. The system displays the committee, its chair, and the rapporteur where
official metadata supports those roles. It explicitly warns that a rapporteur
is not automatically the author of every amendment and does not guess missing
attribution.

### 6. Reusable thematic reporting

Commit: `df90d15` — **Add reusable thematic report generator**

Codex generalized the AI-in-medicine example into a report generator for any
topic and audience profile. It searches official Sejm prints and
interpellations, produces a source-linked narrative, supports PDF import, and
offers follow-up questions.

### 7. RAG correctness hardening

Commit: `48f9c1c` — **Enforce scoped RAG evidence validation**

An audit found that the case-specific question route was not actually scoped
to its case and that the existing validator was not wired into the public
answer path. Codex corrected both issues:

- retrieval is limited to the selected legislative case;
- the model must return structured evidence;
- each cited page must exist;
- each quotation must occur exactly on that page;
- invalid answers are rejected rather than displayed.

This stage included a live model test and a production verification against an
official PDF page.

### 8. Monitoring without paid add-ons

Commit: `3c82b9b` — **Add zero-addon Sejm print monitoring**

To respect the human's cost constraint, Codex implemented recent-print
metadata monitoring inside the existing web process. It runs at startup and
every six hours without a scheduler, worker, or managed database. The UI
exposes the last monitoring result.

### 9. Accessible keyboard control for the 3D tree

Commit: `3495e33` — **Add keyboard navigation to 3D tree**

Codex added two interaction modes:

- **Simple:** arrow-key node navigation, Enter for details, Home to reset;
- **Full 3D:** WASD/arrow camera rotation, zoom, reset, and node stepping.

The implementation added focus management, live accessibility announcements,
visible instructions, selection highlighting, and browser-based interaction
testing.

### 10. English UI with official-source safeguards

Commit: `013f943` — **Add English UI with official-source safeguards**

Codex implemented persistent Polish/English switching across the main
application. The report narrative and AI answer can be English, but official
titles, quotations, process descriptions, and legal text remain in the
language supplied by the official source. The interface explicitly states
that it does not invent unofficial legal translations.

### 11. Competition submission preparation

Commits:

- `a35b540` — **Prepare truthful Build Week submission package**
- `bc4fd47` — **Document GPT-5.6 build-time use with Codex**

Codex checked the official Build Week and Devpost requirements, audited the
existing project description, added an MIT license, prepared the Devpost
write-up, demo script, and submission checklist, and corrected outdated claims
about synthetic data and the runtime model.

GPT-5.6 is accurately described as the model used through Codex to create,
test, debug, deploy, and verify the project. The public runtime is separately
identified as the free-tier `gpt-oss-120b` configuration.

## How GPT-5.6 accelerated the work

Across these Codex sessions, GPT-5.6 helped:

1. turn a broad civic-monitoring idea into a testable vertical slice;
2. design a data model that preserves document and page provenance;
3. identify the trust boundary between AI synthesis and deterministic checks;
4. integrate and inspect public Sejm APIs;
5. diagnose discrepancies between README claims and actual behavior;
6. implement fixes and regression tests;
7. iterate on interaction design and accessibility;
8. verify real behavior in a browser and on the production deployment;
9. maintain a truthful distinction between implemented, partial, and future
   functionality;
10. prepare the repository and Devpost materials for judging.

## Human decisions

The human explicitly decided:

- the target audience and civic/public-interest purpose;
- the AI-in-medicine demonstration scenario;
- that all legislative data must be real and official;
- that answers must expose sources and page numbers;
- that unavailable authorship must not be guessed;
- that the deployment should avoid new add-ons and model charges;
- that reports should work for arbitrary topics;
- that the change history should have an interactive 3D representation;
- that keyboard navigation should have simple and full modes;
- that an English UI must preserve official source-language legal text;
- that the project should be open source and submitted to Build Week.

## Verification evidence

- Public repository: https://github.com/kierepka/SejmWatch
- Public application: https://sejmwatch-c0e8a67cd6b2.herokuapp.com/
- English interface: https://sejmwatch-c0e8a67cd6b2.herokuapp.com/en
- Public Devpost project: https://devpost.com/software/sejmwatch
- Git history: the commits listed above were created during the Codex build
  workflow.
- Automated verification: 13 core tests pass in the current repository.

## Session ID requirement

Devpost requires the `/feedback` Session ID from the primary Codex thread. A
written summary or Git history does not replace that identifier. Run
`/feedback` in the primary build thread and add the returned alphanumeric
Session ID to submission field `27950`.
