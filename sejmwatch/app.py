import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import connect, default_path, init_db
from .ai import (
    AIUnavailable, ask_ai, check_rate_limit, generate_topic_report,
    retrieve_context,
)
from .diffing import compare_documents
from .ingest import download_pdf, import_document
from .official_sync import sync_official_ai_case
from .sejm_api import SejmAPI


BASE = Path(__file__).parent
app = FastAPI(title="SejmWatch", description="Evidence-first legislative change intelligence")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.on_event("startup")
def startup() -> None:
    path = default_path()
    init_db(path)
    if os.getenv("SEJMWATCH_AUTO_SYNC", "1") == "1":
        sync_official_ai_case(path)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with connect() as conn:
        cases = conn.execute(
            "SELECT c.*, COUNT(DISTINCT d.id) document_count, COUNT(DISTINCT ch.id) change_count "
            "FROM cases c LEFT JOIN documents d ON d.case_id=c.id LEFT JOIN changes ch ON ch.case_id=c.id GROUP BY c.id"
        ).fetchall()
    return templates.TemplateResponse(request, "home.html", {"cases": cases})


@app.post("/ask", response_class=HTMLResponse)
def ask_anything(request: Request, question: str = Form(..., max_length=2000)):
    client_id = request.client.host if request.client else "unknown"
    try:
        check_rate_limit(client_id)
        result = ask_ai(
            question, retrieve_context(default_path(), question),
            db_path=default_path(),
        )
        return templates.TemplateResponse(
            request, "global_answer.html", {"question": question, **result}
        )
    except (ValueError, AIUnavailable) as exc:
        return templates.TemplateResponse(
            request,
            "global_answer.html",
            {"question": question, "error": str(exc)},
            status_code=429 if "Limit 10" in str(exc) else 503,
        )
    except httpx.HTTPError:
        return templates.TemplateResponse(
            request,
            "global_answer.html",
            {"question": question, "error": "Darmowy model AI jest chwilowo niedostępny."},
            status_code=502,
        )


@app.get("/sejm", response_class=HTMLResponse)
def sejm_prints(request: Request):
    try:
        api = SejmAPI()
        term = api.term(10)
        prints = api.prints(10, 30)
        return templates.TemplateResponse(
            request, "sejm.html", {"term": term, "prints": prints}
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "sejm.html",
            {"error": f"API Sejmu jest chwilowo niedostępne: {exc}"},
            status_code=502,
        )


@app.get("/reports/new", response_class=HTMLResponse)
def new_report(request: Request):
    return templates.TemplateResponse(request, "report_new.html", {})


@app.get("/reports/topic", response_class=HTMLResponse)
def topic_report(
    request: Request,
    topic: str = Query(..., min_length=2, max_length=160),
    profile: str = Query("obywatel", max_length=120),
):
    client_id = request.client.host if request.client else "unknown"
    try:
        check_rate_limit(client_id, limit=10)
        api = SejmAPI(timeout=45)
        prints = api.search_prints(topic, limit=12)
        interpellations = api.search_interpellations(topic, limit=8)
        process = None
        if prints:
            process_number = (prints[0].get("processPrint") or [None])[0]
            if process_number:
                try:
                    process = api.process(str(process_number), 10)
                except Exception:
                    process = None
        result = generate_topic_report(
            topic, profile, prints, interpellations, process
        )
        return templates.TemplateResponse(
            request, "report.html",
            {
                "topic": topic, "profile": profile, "prints": prints,
                "interpellations": interpellations, "process": process,
                **result,
            },
        )
    except (ValueError, AIUnavailable) as exc:
        return templates.TemplateResponse(
            request, "report.html",
            {"topic": topic, "profile": profile, "error": str(exc)},
            status_code=429 if "Limit 10" in str(exc) else 503,
        )
    except httpx.HTTPError:
        return templates.TemplateResponse(
            request, "report.html",
            {
                "topic": topic, "profile": profile,
                "error": "Nie udało się pobrać danych lub wygenerować raportu.",
            },
            status_code=502,
        )
@app.get("/topics/ai-medicine", response_class=HTMLResponse)
def ai_medicine_topic(request: Request):
    try:
        api = SejmAPI()
        process = api.process("2443", 10)
        prints = [
            api.print_details(number, 10)
            for number in ("2443", "2614", "2614-A", "2731", "2762")
        ]
        interpellations = [
            api.interpellation(number, 10) for number in (9163, 16033)
        ]
        return templates.TemplateResponse(
            request,
            "topic_ai_medicine.html",
            {
                "process": process,
                "prints": prints,
                "interpellations": interpellations,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "topic_ai_medicine.html",
            {"error": f"Nie udało się pobrać aktualnych danych: {exc}"},
            status_code=502,
        )


@app.post("/sejm/import/{number}")
def import_sejm_print(number: str):
    try:
        api = SejmAPI()
        details = api.print_details(number, 10)
        pdf_url = api.primary_pdf(details)
        if not pdf_url:
            raise ValueError("Druk nie ma załącznika PDF")
        content = download_pdf(pdf_url)
        process = details.get("processPrint") or [number]
        case_id = f"sejm-10-{process[0]}"
        document_id = f"druk-10-{number}"
        import_document(
            default_path(),
            case_id,
            details["title"],
            document_id,
            f"Druk nr {number}",
            pdf_url,
            content,
        )
        with connect() as conn:
            previous = conn.execute(
                "SELECT id FROM documents WHERE case_id=? AND id<>? ORDER BY created_at DESC LIMIT 1",
                (case_id, document_id),
            ).fetchone()
        if previous:
            compare_documents(default_path(), previous["id"], document_id)
        return RedirectResponse(f"/cases/{case_id}", status_code=303)
    except Exception as exc:
        raise HTTPException(422, f"Nie udało się zaimportować druku: {exc}")


@app.get("/cases/{case_id}", response_class=HTMLResponse)
def case_view(request: Request, case_id: str):
    with connect() as conn:
        case = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not case:
            raise HTTPException(404, "Case not found")
        documents = conn.execute("SELECT * FROM documents WHERE case_id=? ORDER BY created_at, id", (case_id,)).fetchall()
        changes = conn.execute(
            "SELECT ch.*, d.source_url FROM changes ch JOIN documents d ON d.id=ch.new_document_id "
            "WHERE ch.case_id=? ORDER BY ch.id", (case_id,)
        ).fetchall()
    return templates.TemplateResponse(request, "case.html", {"case": case, "documents": documents, "changes": changes})


@app.get("/cases/{case_id}/tree", response_class=HTMLResponse)
def change_tree(request: Request, case_id: str):
    with connect() as conn:
        case = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
        if not case:
            raise HTTPException(404, "Case not found")
        documents = conn.execute(
            "SELECT id, version_label, source_url FROM documents "
            "WHERE case_id=? ORDER BY created_at, id", (case_id,)
        ).fetchall()
        rows = conn.execute(
            "SELECT id, new_document_id, section_key, change_type, new_page, "
            "substr(COALESCE(new_text, old_text),1,500) summary "
            "FROM changes WHERE case_id=? AND section_key LIKE 'art.%' "
            "ORDER BY id LIMIT 350", (case_id,)
        ).fetchall()
        if not rows:
            rows = conn.execute(
                "SELECT id, new_document_id, section_key, change_type, new_page, "
                "substr(COALESCE(new_text, old_text),1,500) summary "
                "FROM changes WHERE case_id=? ORDER BY id LIMIT 250", (case_id,)
            ).fetchall()
    nodes = [{
        "id": "case", "parent": None, "kind": "case",
        "label": case["title"], "detail": "Proces legislacyjny",
    }]
    for doc in documents:
        nodes.append({
            "id": doc["id"], "parent": "case", "kind": "document",
            "label": doc["version_label"], "detail": doc["id"], "url": doc["source_url"],
        })
    for row in rows:
        nodes.append({
            "id": f"change-{row['id']}", "parent": row["new_document_id"],
            "kind": row["change_type"], "label": row["section_key"],
            "detail": row["summary"], "page": row["new_page"],
        })
    responsibility = None
    if case_id == "sejm-10-2443":
        try:
            api = SejmAPI()
            committee = api.committee("CNT", 10)
            rapporteur = api.member(257, 10)
            chair = next(
                (m for m in committee["members"] if m.get("function") == "przewodniczący"),
                None,
            )
            responsibility = {
                "rapporteur": rapporteur,
                "chair": chair,
                "committee": committee,
            }
        except Exception:
            responsibility = None
    return templates.TemplateResponse(
        request, "tree.html",
        {"case": case, "nodes": nodes, "responsibility": responsibility},
    )


@app.post("/cases/{case_id}/ask", response_class=HTMLResponse)
def ask(request: Request, case_id: str, question: str = Form(...)):
    try:
        client_id = request.client.host if request.client else "unknown"
        check_rate_limit(client_id)
        context = retrieve_context(
            default_path(), question, case_id=case_id
        )
        result = ask_ai(question, context, db_path=default_path())
        return templates.TemplateResponse(
            request, "global_answer.html", {"question": question, **result}
        )
    except (ValueError, AIUnavailable) as exc:
        return templates.TemplateResponse(
            request,
            "global_answer.html",
            {"question": question, "error": str(exc)},
            status_code=429 if "Limit 10" in str(exc) else 503,
        )


@app.get("/health")
def health():
    return {"status": "ok", "storage": "sqlite-ephemeral"}
