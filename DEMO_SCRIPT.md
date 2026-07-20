# SejmWatch demo script — under 3 minutes

The narration should be recorded in English. Keep the browser zoom large enough
for page citations to remain readable.

## 0:00–0:20 — problem

**Screen:** English home page.

> Polish bills evolve through long parliamentary PDFs and committee reports.
> People affected by those changes should not need to compare every version
> manually—or trust an AI summary without evidence. SejmWatch makes each
> important claim traceable to an official page.

## 0:20–0:45 — official data

**Screen:** Latest prints, then the monitored AI systems bill.

> The application reads live metadata from the official Sejm API. The demo
> uses real parliamentary prints, not mock legislation. PDFs are downloaded
> from official HTTPS links, hashed, and extracted page by page.

## 0:45–1:15 — legislative change intelligence

**Screen:** Verified changes, then the 3D tree.

> SejmWatch links versions belonging to one legislative case and compares them
> deterministically at article level. The change tree can be explored with the
> mouse or keyboard. Official data identifies the responsible committee and
> rapporteur, but the system does not invent the author of an amendment when
> the source does not provide that attribution.

## 1:15–1:50 — evidence-backed question

**Screen:** Ask one prepared question and show the answer and source.

> Retrieval is scoped to this legislative case. The model receives relevant
> source pages and returns a structured answer. SejmWatch displays it only
> after verifying that the cited page exists and the exact quotation occurs on
> that page. The model explains; deterministic code verifies.

Use a question tested immediately before recording so the free provider does
not consume demo time with a weak query.

## 1:50–2:15 — thematic report and bilingual UI

**Screen:** Report generator and English source-language notice.

> Users can generate reports for any topic and audience, such as AI in
> medicine or hospital cybersecurity. The interface and report narrative can
> be English, while official Polish legal titles and quotations are never
> machine-translated unless the source provides an official translation.

## 2:15–2:45 — Codex and GPT-5.6

**Screen:** Git history, tests, and the exact verified GPT-5.6 integration or
artifact.

> Codex was my implementation partner for architecture, official API
> integration, evidence validation, tests, accessible 3D interaction,
> bilingual UI, deployment, and live verification. I made the product
> decisions around scope, source integrity, attribution, and cost. [Add one
> exact, truthful sentence explaining the meaningful GPT-5.6 task and show its
> output being validated.]

## 2:45–2:58 — close

**Screen:** Answer with citation, then repository URL.

> SejmWatch is an open-source, evidence-first assistant for understanding how
> legislation changes—without asking users to choose between accessibility and
> verifiability.

## Recording checklist

- Public YouTube video.
- Duration below 3:00.
- Spoken audio explicitly covers both Codex and GPT-5.6.
- Show the working product, not slides alone.
- Keep official source URL, page number, and quotation visible.
- Do not say that every change is attributed to an MP.
- Do not say that the Heroku Basic dyno is free.
- Do not describe the current official demo as synthetic.
