import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .db import connect


ARTICLE = re.compile(r"(?im)^(art\.\s*\d+[a-z]*\.?)(.*?)(?=^art\.\s*\d+[a-z]*\.?|\Z)", re.S)


@dataclass
class Section:
    key: str
    text: str
    page: int


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sections_from_pages(pages: List[Tuple[int, str]]) -> Dict[str, Section]:
    sections: Dict[str, Section] = {}
    for page_number, page_text in pages:
        matches = list(ARTICLE.finditer(page_text))
        if not matches:
            key = f"page-{page_number}"
            sections[key] = Section(key, normalize(page_text), page_number)
            continue
        for match in matches:
            key = normalize(match.group(1)).lower().rstrip(".")
            text = normalize(match.group(0))
            if key in sections:
                sections[key].text += " " + text
            else:
                sections[key] = Section(key, text, page_number)
    return sections


def compare_documents(db_path: str, old_id: str, new_id: str) -> List[dict]:
    with connect(db_path) as conn:
        docs = conn.execute(
            "SELECT id, case_id FROM documents WHERE id IN (?, ?)", (old_id, new_id)
        ).fetchall()
        if len(docs) != 2 or docs[0]["case_id"] != docs[1]["case_id"]:
            raise ValueError("Documents must exist and belong to the same legislative case")
        case_id = docs[0]["case_id"]
        old_pages = conn.execute(
            "SELECT page_number, text FROM pages WHERE document_id=? ORDER BY page_number", (old_id,)
        ).fetchall()
        new_pages = conn.execute(
            "SELECT page_number, text FROM pages WHERE document_id=? ORDER BY page_number", (new_id,)
        ).fetchall()
        old = sections_from_pages([(r[0], r[1]) for r in old_pages])
        new = sections_from_pages([(r[0], r[1]) for r in new_pages])
        changes = []
        for key in sorted(set(old) | set(new)):
            before, after = old.get(key), new.get(key)
            if before and after and before.text == after.text:
                continue
            kind = "added" if not before else "removed" if not after else "modified"
            item = {
                "section_key": key,
                "change_type": kind,
                "old_text": before.text if before else None,
                "new_text": after.text if after else None,
                "new_page": after.page if after else None,
            }
            changes.append(item)
            conn.execute(
                "INSERT INTO changes(case_id, old_document_id, new_document_id, section_key, "
                "change_type, old_text, new_text, new_page) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(old_document_id, new_document_id, section_key) DO UPDATE SET "
                "change_type=excluded.change_type, old_text=excluded.old_text, "
                "new_text=excluded.new_text, new_page=excluded.new_page",
                (case_id, old_id, new_id, key, kind, item["old_text"], item["new_text"], item["new_page"]),
            )
        return changes

