import re
from typing import List

from .db import connect


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
