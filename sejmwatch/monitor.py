import json
import os
import threading
from typing import Dict

from .db import connect, default_path
from .sejm_api import SejmAPI


_stop = threading.Event()
_thread = None


def sync_print_metadata(db_path: str = None, limit: int = 300) -> Dict[str, int]:
    """Store a recent snapshot and detect newly observed Sejm prints."""
    path = db_path or default_path()
    rows = SejmAPI(timeout=45).prints(10, limit)
    new_count = 0
    with connect(path) as conn:
        for row in rows:
            exists = conn.execute(
                "SELECT 1 FROM monitored_prints WHERE term=? AND number=?",
                (10, str(row["number"])),
            ).fetchone()
            if not exists:
                new_count += 1
            conn.execute(
                "INSERT INTO monitored_prints"
                "(term,number,title,delivery_date,process_print) VALUES (?,?,?,?,?) "
                "ON CONFLICT(term,number) DO UPDATE SET "
                "title=excluded.title,delivery_date=excluded.delivery_date,"
                "process_print=excluded.process_print,last_seen_at=CURRENT_TIMESTAMP",
                (
                    10, str(row["number"]), row.get("title", ""),
                    row.get("deliveryDate"),
                    json.dumps(row.get("processPrint") or []),
                ),
            )
        conn.execute(
            "INSERT INTO monitor_runs(print_count,new_count,status) VALUES (?,?,?)",
            (len(rows), new_count, "ok"),
        )
    return {"print_count": len(rows), "new_count": new_count}


def _monitor_loop() -> None:
    interval = max(900, int(os.getenv("SEJMWATCH_POLL_SECONDS", "21600")))
    while not _stop.wait(interval):
        try:
            sync_print_metadata()
        except Exception:
            with connect() as conn:
                conn.execute(
                    "INSERT INTO monitor_runs(print_count,new_count,status) "
                    "VALUES (0,0,'error')"
                )


def start_monitor() -> None:
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    try:
        sync_print_metadata()
    except Exception:
        pass
    _thread = threading.Thread(
        target=_monitor_loop, name="sejmwatch-monitor", daemon=True
    )
    _thread.start()


def stop_monitor() -> None:
    _stop.set()
