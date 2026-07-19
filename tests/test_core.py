import sqlite3
import time

import pytest

from sejmwatch.db import init_db
from sejmwatch.diffing import compare_documents, sections_from_pages
from sejmwatch.evidence import EvidenceError, validate_evidence
from sejmwatch.ingest import import_document
from sejmwatch.models import Evidence
from sejmwatch.rag import search
from sejmwatch.sejm_api import SejmAPI
from sejmwatch.ai import check_rate_limit, retrieve_context


@pytest.fixture()
def db(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    pages_v1 = [
        "Art. 1. Ustawa określa obowiązki podmiotów leczniczych.",
        "Art. 14. Okres dostosowawczy wynosi 24 miesiące.",
    ]
    pages_v2 = [
        "Art. 1. Ustawa określa obowiązki podmiotów leczniczych i dostawców.",
        "Art. 14. Okres dostosowawczy wynosi 12 miesięcy.\n"
        "Art. 15. Dostawca prowadzi rejestr incydentów.",
    ]
    import_document(
        path, "test-case", "Test zmian", "test-v1", "v1",
        "https://example.test/v1.pdf", b"test-v1", pages=pages_v1,
    )
    import_document(
        path, "test-case", "Test zmian", "test-v2", "v2",
        "https://example.test/v2.pdf", b"test-v2", pages=pages_v2,
    )
    compare_documents(path, "test-v1", "test-v2")
    return path


def test_article_diff_detects_added_and_modified(db):
    changes = compare_documents(db, "test-v1", "test-v2")
    kinds = {(item["section_key"], item["change_type"]) for item in changes}
    assert ("art. 14", "modified") in kinds
    assert ("art. 15", "added") in kinds


def test_valid_quote_is_accepted(db):
    validate_evidence(db, [Evidence(
        document_id="test-v2", page=2,
        quote="Okres dostosowawczy wynosi 12 miesięcy"
    )])


def test_nonexistent_page_is_rejected(db):
    with pytest.raises(EvidenceError, match="does not exist"):
        validate_evidence(db, [Evidence(
            document_id="test-v2", page=99, quote="dowolny cytat"
        )])


def test_hallucinated_quote_is_rejected(db):
    with pytest.raises(EvidenceError, match="not found"):
        validate_evidence(db, [Evidence(
            document_id="test-v2", page=2,
            quote="Karę podwyższono do miliona złotych"
        )])


def test_documents_from_different_cases_are_rejected(db):
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO cases(id,title) VALUES ('other','Other')")
        conn.execute("INSERT INTO documents VALUES ('other-v1','other','v1','https://example.test','unique',CURRENT_TIMESTAMP)")
    with pytest.raises(ValueError, match="same legislative case"):
        compare_documents(db, "test-v1", "other-v1")


def test_fts_search_is_scoped_to_case(db):
    results = search(db, "okres dostosowawczy", "test-case")
    assert results
    assert all(row["document_id"].startswith("test-") for row in results)


def test_section_parser_preserves_page_number():
    result = sections_from_pages([(8, "Art. 14. Termin wynosi 12 miesięcy.")])
    assert result["art. 14"].page == 8


def test_sejm_pdf_url_uses_official_api():
    details = {
        "term": 10,
        "number": "1527-A",
        "attachments": ["1527-A.docx", "1527-A.pdf"],
    }
    assert SejmAPI().primary_pdf(details) == (
        "https://api.sejm.gov.pl/sejm/term10/prints/1527-A/1527-A.pdf"
    )


def test_global_context_search_returns_page_sources(db):
    results = retrieve_context(db, "okres dostosowawczy")
    assert results
    assert results[0]["page_number"] >= 1


def test_question_rate_limit():
    client = f"test-{time.time_ns()}"
    for _ in range(10):
        check_rate_limit(client)
    with pytest.raises(ValueError, match="Limit 10"):
        check_rate_limit(client)
