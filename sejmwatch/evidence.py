from typing import Iterable

from .db import connect
from .models import Evidence


class EvidenceError(ValueError):
    pass


def validate_evidence(db_path: str, evidence: Iterable[Evidence]) -> None:
    items = list(evidence)
    if not items:
        raise EvidenceError("At least one citation is required")
    with connect(db_path) as conn:
        for item in items:
            row = conn.execute(
                "SELECT text FROM pages WHERE document_id=? AND page_number=?",
                (item.document_id, item.page),
            ).fetchone()
            if not row:
                raise EvidenceError(
                    f"Page {item.page} does not exist in {item.document_id}"
                )
            quote = " ".join(item.quote.split()).lower()
            page = " ".join(row["text"].split()).lower()
            if quote not in page:
                raise EvidenceError(
                    f"Quote was not found on page {item.page} of {item.document_id}"
                )

