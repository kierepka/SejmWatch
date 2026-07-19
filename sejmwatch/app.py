import os
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import connect, default_path, init_db
from .demo import seed
from .diffing import compare_documents
from .ingest import download_pdf, import_document
from .rag import answer_question
from .sejm_api import SejmAPI


BASE = Path(__file__).parent
app = FastAPI(title="SejmWatch", description="Evidence-first legislative change intelligence")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.on_event("startup")
def startup() -> None:
    path = default_path()
    init_db(path)
    with connect(path) as conn:
        empty = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
    if empty and os.getenv("SEJMWATCH_AUTO_SEED", "1") == "1":
        seed(path)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with connect() as conn:
        cases = conn.execute(
            "SELECT c.*, COUNT(DISTINCT d.id) document_count, COUNT(DISTINCT ch.id) change_count "
            "FROM cases c LEFT JOIN documents d ON d.case_id=c.id LEFT JOIN changes ch ON ch.case_id=c.id GROUP BY c.id"
        ).fetchall()
    return templates.TemplateResponse(request, "home.html", {"cases": cases})


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


@app.post("/cases/{case_id}/ask", response_class=HTMLResponse)
def ask(request: Request, case_id: str, question: str = Form(...)):
    try:
        answer = answer_question(default_path(), question, case_id)
        return templates.TemplateResponse(request, "answer.html", {"case_id": case_id, "question": question, "answer": answer})
    except ValueError as exc:
        return templates.TemplateResponse(request, "answer.html", {"case_id": case_id, "question": question, "error": str(exc)}, status_code=422)


@app.get("/health")
def health():
    return {"status": "ok", "storage": "sqlite-ephemeral"}
