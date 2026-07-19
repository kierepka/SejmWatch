import sqlite3

import pytest

from sejmwatch.db import init_db
from sejmwatch.demo import seed
from sejmwatch.diffing import compare_documents, sections_from_pages
from sejmwatch.evidence import EvidenceError, validate_evidence
from sejmwatch.models import Evidence
from sejmwatch.rag import search
from sejmwatch.sejm_api import SejmAPI


@pytest.fixture()
def db(tmp_path):
    path = str(tmp_path / "test.db")
    seed(path)
    return path


def test_article_diff_detects_added_and_modified(db):
    changes = compare_documents(db, "druk-demo-v1", "druk-demo-v2")
    kinds = {(item["section_key"], item["change_type"]) for item in changes}
    assert ("art. 14", "modified") in kinds
    assert ("art. 15", "added") in kinds


def test_valid_quote_is_accepted(db):
    validate_evidence(db, [Evidence(
        document_id="druk-demo-v2", page=2,
        quote="Okres dostosowawczy wynosi 12 miesięcy"
    )])


def test_nonexistent_page_is_rejected(db):
    with pytest.raises(EvidenceError, match="does not exist"):
        validate_evidence(db, [Evidence(
            document_id="druk-demo-v2", page=99, quote="dowolny cytat"
        )])


def test_hallucinated_quote_is_rejected(db):
    with pytest.raises(EvidenceError, match="not found"):
        validate_evidence(db, [Evidence(
            document_id="druk-demo-v2", page=2,
            quote="Karę podwyższono do miliona złotych"
        )])


def test_documents_from_different_cases_are_rejected(db):
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO cases(id,title) VALUES ('other','Other')")
        conn.execute("INSERT INTO documents VALUES ('other-v1','other','v1','https://example.test','unique',CURRENT_TIMESTAMP)")
    with pytest.raises(ValueError, match="same legislative case"):
        compare_documents(db, "druk-demo-v1", "other-v1")


def test_fts_search_is_scoped_to_case(db):
    results = search(db, "okres dostosowawczy", "cyber-health")
    assert results
    assert all(row["document_id"].startswith("druk-demo") for row in results)


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
