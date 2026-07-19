import hashlib
import re
from pathlib import Path
from typing import List, Optional

import httpx

from .db import connect, replace_pages


def extract_pdf_pages(content: bytes) -> List[str]:
    import fitz

    document = fitz.open(stream=content, filetype="pdf")
    return [page.get_text("text").strip() for page in document]


def import_document(
    db_path: str,
    case_id: str,
    case_title: str,
    document_id: str,
    version_label: str,
    source_url: str,
    content: bytes,
    pages: Optional[List[str]] = None,
) -> str:
    digest = hashlib.sha256(content).hexdigest()
    extracted = pages if pages is not None else extract_pdf_pages(content)
    if not extracted or not any(page.strip() for page in extracted):
        raise ValueError("PDF does not contain extractable text; OCR is outside MVP scope")
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO cases(id, title) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET title=excluded.title",
            (case_id, case_title),
        )
        existing = conn.execute(
            "SELECT id FROM documents WHERE sha256 = ?", (digest,)
        ).fetchone()
        if existing and existing["id"] != document_id:
            raise ValueError(f"This exact document already exists as {existing['id']}")
        conn.execute(
            "INSERT INTO documents(id, case_id, version_label, source_url, sha256) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
            "version_label=excluded.version_label, source_url=excluded.source_url, sha256=excluded.sha256",
            (document_id, case_id, version_label, source_url, digest),
        )
        replace_pages(conn, document_id, extracted)
    return digest


def download_pdf(url: str) -> bytes:
    if not re.match(r"^https://", url):
        raise ValueError("Only HTTPS document URLs are accepted")
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" not in content_type.lower() and not response.content.startswith(b"%PDF"):
        raise ValueError("URL did not return a PDF")
    return response.content

