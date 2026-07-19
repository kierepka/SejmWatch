from typing import Iterable

from .db import connect, init_db
from .diffing import compare_documents
from .ingest import download_pdf, import_document
from .sejm_api import SejmAPI


AI_PROCESS_PRINTS = ("2443", "2614")


def sync_official_ai_case(
    db_path: str, print_numbers: Iterable[str] = AI_PROCESS_PRINTS
) -> None:
    """Populate the canonical AI case exclusively from official Sejm PDFs."""
    init_db(db_path)
    api = SejmAPI()
    process = api.process("2443", 10)
    imported = []
    for number in print_numbers:
        details = api.print_details(number, 10)
        pdf_url = api.primary_pdf(details)
        if not pdf_url:
            raise ValueError(f"Official print {number} has no PDF attachment")
        document_id = f"druk-10-{number}"
        with connect(db_path) as conn:
            exists = conn.execute(
                "SELECT 1 FROM documents WHERE id=?", (document_id,)
            ).fetchone()
        if not exists:
            import_document(
                db_path=db_path,
                case_id="sejm-10-2443",
                case_title=process["title"],
                document_id=document_id,
                version_label=f"Druk nr {number}",
                source_url=pdf_url,
                content=download_pdf(pdf_url),
            )
        imported.append(document_id)
    for old_id, new_id in zip(imported, imported[1:]):
        compare_documents(db_path, old_id, new_id)

