import json
import os
import re
from typing import List

from .db import connect
from .evidence import validate_evidence
from .models import Answer, Evidence


def search(db_path: str, query: str, case_id: str, limit: int = 5) -> List[dict]:
    terms = [term for term in re.findall(r"\w+", query.lower()) if len(term) > 2]
    if not terms:
        return []
    fts_query = " OR ".join(f'"{term}"' for term in terms[:8])
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT f.document_id, f.page_number, f.text, d.source_url, bm25(pages_fts) score "
            "FROM pages_fts f JOIN documents d ON d.id=f.document_id "
            "WHERE pages_fts MATCH ? AND d.case_id=? ORDER BY score LIMIT ?",
            (fts_query, case_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def answer_question(db_path: str, question: str, case_id: str) -> Answer:
    context = search(db_path, question, case_id)
    if not context:
        raise ValueError("No relevant evidence found")
    if not os.getenv("OPENAI_API_KEY"):
        first = context[0]
        quote = " ".join(first["text"].split())[:280]
        answer = Answer(
            answer="Tryb demo: znaleziono poniższy fragment źródłowy. Skonfiguruj OPENAI_API_KEY, aby otrzymać syntezę GPT-5.6.",
            evidence=[Evidence(document_id=first["document_id"], page=first["page_number"], quote=quote, url=first["source_url"])],
            confidence="medium",
        )
        validate_evidence(db_path, answer.evidence)
        return answer

    from openai import OpenAI

    payload = [{"document_id": r["document_id"], "page": r["page_number"], "url": r["source_url"], "text": r["text"]} for r in context]
    client = OpenAI()
    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
        input=[
            {"role": "system", "content": "Answer in Polish using only supplied pages. Every material claim needs a short verbatim quote. If evidence is insufficient, say so. This is information, not legal advice."},
            {"role": "user", "content": f"Question: {question}\nPages: {json.dumps(payload, ensure_ascii=False)}"},
        ],
        text_format=Answer,
    )
    answer = response.output_parsed
    validate_evidence(db_path, answer.evidence)
    return answer

