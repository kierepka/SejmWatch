# SejmWatch — 2:50 demo storyboard

The competition requires a public YouTube video shorter than three minutes
with spoken explanation of both Codex and GPT-5.6. Record the narration in
English.

| Time | Visual | Action |
|---|---|---|
| 0:00–0:18 | `01-home-en.png` | Start on the English home page and move the pointer over the evidence-first question box. |
| 0:18–0:38 | `02-official-prints-en.png` | Show live Sejm metadata, monitoring status, and an official print title. |
| 0:38–1:02 | `03-change-timeline-en.png` | Open the AI systems bill, point to two official versions and 771 detected changes. |
| 1:02–1:28 | `04-3d-tree-en.png` | Switch Simple/Full 3D, press an arrow key, and show the responsibility panel briefly. |
| 1:28–1:58 | `05-verified-answer-en.png` | Ask the prepared question; highlight the answer, page 171, exact quote, and official-PDF link. |
| 1:58–2:18 | `06-report-builder-en.png` | Show arbitrary-topic reporting and the source-language safeguard. |
| 2:18–2:42 | Codex/Git history | Show `CODEX_BUILD_LOG.md`, the commit history, and the passing tests. |
| 2:42–2:55 | Home/repository | Finish on the product name and repository URL. |

## Narration

### 0:00–0:18 — problem

> Polish bills evolve through long parliamentary PDFs and committee reports.
> People affected by those changes should not need to compare every version
> manually—or trust an AI summary without evidence. SejmWatch makes every
> important claim traceable to an official page.

### 0:18–0:38 — official data

> SejmWatch reads live metadata from the official Sejm API. The demo uses real
> parliamentary prints, not mock legislation. Official PDFs are downloaded,
> hashed, and extracted page by page.

### 0:38–1:02 — changes between versions

> Documents belonging to the same legislative case are linked and compared
> deterministically at article level. Here we follow the Polish government
> bill on artificial intelligence systems through two official versions and
> hundreds of detected textual changes.

### 1:02–1:28 — 3D process and responsibility

> The process can be explored as a keyboard-accessible 3D change tree, using a
> simple navigation mode or full camera controls. Official data identifies the
> committee and rapporteur. When the source does not identify the author of a
> particular amendment, SejmWatch does not guess.

### 1:28–1:58 — evidence-backed RAG

> Retrieval is scoped to this legislative case. The model explains the
> retrieved material, but deterministic code verifies it. An answer is shown
> only if the cited page exists and the exact quotation occurs on that page.
> Here the answer links directly to page 171 of the official PDF.

### 1:58–2:18 — reports and languages

> Users can create a report for any topic and audience, such as AI in medicine
> or hospital cybersecurity. The interface and narrative can be English, while
> titles, quotations, and legal text retain the exact language of the official
> source unless an official translation exists.

### 2:18–2:42 — Codex and GPT-5.6

> SejmWatch was created entirely through Codex sessions using GPT-5.6. Codex
> and GPT-5.6 helped turn the idea into the architecture, official API
> integration, evidence validation, tests, accessible 3D interaction,
> bilingual UI, deployment, and live verification. I made the product
> decisions about scope, source integrity, attribution, and cost.

> GPT-5.6 was the build-time model inside Codex. The public runtime separately
> uses the free-tier gpt-oss-120b model so the demo does not add model charges.

### 2:42–2:55 — close

> SejmWatch is an open-source, evidence-first assistant for understanding how
> legislation changes—without asking users to choose between accessibility and
> verifiability.

## Editing notes

- Use 16:9 at 1920×1080 or 1440×810.
- Keep transitions under 0.4 seconds.
- Use cursor zoom only around the version count, source page, and quotation.
- Do not place music above the narration.
- Show the Codex build log and a terminal with `13 passed`.
- End before 2:58 to leave a safety margin below the three-minute limit.
