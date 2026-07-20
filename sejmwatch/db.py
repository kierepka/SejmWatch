import os
import sqlite3
from pathlib import Path
from typing import Iterable, Optional


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(id),
  version_label TEXT NOT NULL,
  source_url TEXT NOT NULL,
  sha256 TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS pages (
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  page_number INTEGER NOT NULL CHECK(page_number > 0),
  text TEXT NOT NULL,
  PRIMARY KEY(document_id, page_number)
);
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
  document_id UNINDEXED, page_number UNINDEXED, text,
  tokenize='unicode61 remove_diacritics 2'
);
CREATE TABLE IF NOT EXISTS changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL REFERENCES cases(id),
  old_document_id TEXT NOT NULL REFERENCES documents(id),
  new_document_id TEXT NOT NULL REFERENCES documents(id),
  section_key TEXT NOT NULL,
  change_type TEXT NOT NULL,
  old_text TEXT,
  new_text TEXT,
  new_page INTEGER,
  UNIQUE(old_document_id, new_document_id, section_key)
);
CREATE TABLE IF NOT EXISTS monitored_prints (
  term INTEGER NOT NULL,
  number TEXT NOT NULL,
  title TEXT NOT NULL,
  delivery_date TEXT,
  process_print TEXT,
  first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(term, number)
);
CREATE TABLE IF NOT EXISTS monitor_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  print_count INTEGER NOT NULL,
  new_count INTEGER NOT NULL,
  status TEXT NOT NULL
);
"""


def default_path() -> str:
    return os.getenv("SEJMWATCH_DB", "data/sejmwatch.db")


def connect(path: Optional[str] = None) -> sqlite3.Connection:
    db_path = path or default_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Optional[str] = None) -> None:
    with connect(path) as conn:
        conn.executescript(SCHEMA)


def replace_pages(conn: sqlite3.Connection, document_id: str, pages: Iterable[str]) -> None:
    conn.execute("DELETE FROM pages_fts WHERE document_id = ?", (document_id,))
    conn.execute("DELETE FROM pages WHERE document_id = ?", (document_id,))
    for number, text in enumerate(pages, start=1):
        conn.execute(
            "INSERT INTO pages(document_id, page_number, text) VALUES (?, ?, ?)",
            (document_id, number, text),
        )
        conn.execute(
            "INSERT INTO pages_fts(document_id, page_number, text) VALUES (?, ?, ?)",
            (document_id, number, text),
        )
