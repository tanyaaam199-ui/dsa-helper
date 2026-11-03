import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

import agent_core
from agent_core import new_session, run_turn_stream
from flashcards import get_daily_flashcards, generate_ai_flashcards

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="TanDSA - AI DSA Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}  # session_id -> conversation history


class ChatIn(BaseModel):
    session_id: str
    message: str
    mode: Optional[str] = None
    model: Optional[str] = None


class CodeRunIn(BaseModel):
    code: str
    timeout: Optional[float] = 4.0


class ModelSetIn(BaseModel):
    model: str


@app.get("/")
def home():
    for p in [
        BASE_DIR / "public" / "index.html",
        BASE_DIR / "static" / "index.html",
        Path.cwd() / "public" / "index.html",
        Path.cwd() / "static" / "index.html",
    ]:
        if p.exists():
            return HTMLResponse(content=p.read_text(encoding="utf-8"))
    return HTMLResponse("<!DOCTYPE html><html><body><h1>TanDSA Backend Running</h1><p>Static index.html not found.</p></body></html>")


@app.post("/chat")
def chat(body: ChatIn):
    messages = sessions.setdefault(body.session_id, new_session())

    def event_stream():
        for event in run_turn_stream(messages, body.message, mode_override=body.mode, model_override=body.model):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@app.get("/api/topics")
def list_topics():
    """Lists categorized DSA study notes available in the local knowledge base."""
    notes_dir = BASE_DIR / "notes"
    if not notes_dir.exists():
        return {"categories": []}

    CATEGORY_METAS = {
        "arrays_and_strings": {"title": "Arrays & Strings", "icon": "", "order": 1},
        "linked_lists": {"title": "Linked Lists", "icon": "", "order": 2},
        "trees": {"title": "Trees & Heaps", "icon": "", "order": 3},
        "searching": {"title": "Searching & Binary Search", "icon": "", "order": 4},
        "hashing": {"title": "Hashing & Maps", "icon": "", "order": 5},
        "graphs": {"title": "Graphs & Networks", "icon": "", "order": 6},
    }

    groups = {}

    for path in sorted(notes_dir.rglob("*.md")):
        rel = path.relative_to(notes_dir)
        parent_name = rel.parent.name.strip()
        if not parent_name or str(rel.parent) == ".":
            cat_key = "graphs" if "graph" in rel.stem.lower() else "general"
        else:
            cat_key = parent_name

        try:
            content = path.read_text(encoding="utf-8").strip()
            first_line = content.splitlines()[0] if content else ""
            title = first_line.lstrip("# ").strip() or path.stem.replace("_", " ").title()

            # Extract first summary paragraph if available
            summary = ""
            for line in content.splitlines()[1:]:
                line = line.strip()
                if line and not line.startswith("#"):
                    summary = line
                    break
        except Exception:
            title = path.stem.replace("_", " ").title()
            summary = ""

        cat_meta = CATEGORY_METAS.get(cat_key, {"title": cat_key.replace("_", " ").title(), "icon": "", "order": 99})

        if cat_key not in groups:
            groups[cat_key] = {
                "key": cat_key,
                "title": cat_meta["title"],
                "icon": cat_meta["icon"],
                "order": cat_meta["order"],
                "topics": [],
            }

        groups[cat_key]["topics"].append({
            "id": str(rel),
            "name": path.stem,
            "title": title,
            "summary": summary[:140] + ("..." if len(summary) > 140 else ""),
            "path": str(rel),
        })

    sorted_categories = sorted(groups.values(), key=lambda c: c["order"])
    return {"categories": sorted_categories}


@app.get("/api/topic/{file_path:path}")
def get_topic_content(file_path: str):
    """Returns markdown note content for instant cheat sheet viewing."""
    # Prevent path traversal
    safe_path = (BASE_DIR / "notes" / file_path).resolve()
    if not str(safe_path).startswith(str((BASE_DIR / "notes").resolve())) or not safe_path.exists():
        raise HTTPException(status_code=404, detail="Topic note not found")

    content = safe_path.read_text(encoding="utf-8")
    return {"path": file_path, "content": content}


class KeySetIn(BaseModel):
    groq_api_key: str


@app.get("/api/models")
def get_models():
    """Returns currently selected model and available Local & Cloud Llama models."""
    available = []
    try:
        import ollama
        resp = ollama.list()
        for m in getattr(resp, "models", []):
            name = getattr(m, "model", None) or getattr(m, "name", None)
            if name and name not in available:
                available.append(name)
    except Exception:
        pass

    if not available:
        available.append("llama3.2:3b (Local Mac)")
    else:
        available = [f"{m} (Local Mac)" if "(" not in m else m for m in available]

    has_groq = bool(os.getenv("GROQ_API_KEY"))
    if has_groq:
        cloud_models = [
            "llama-3.3-70b-versatile (Groq Cloud)",
            "llama-3.1-8b-instant (Groq Cloud)",
        ]
        for cm in cloud_models:
            if cm not in available:
                available.append(cm)

    return {
        "current": agent_core.MODEL,
        "available": available,
        "has_groq": has_groq,
    }


@app.post("/api/set-groq-key")
def set_groq_key(body: KeySetIn):
    key = body.groq_api_key.strip()
    os.environ["GROQ_API_KEY"] = key
    env_file = BASE_DIR / ".env"
    env_file.write_text(f"GROQ_API_KEY={key}\n", encoding="utf-8")
    return {"status": "ok", "has_groq": bool(key)}


@app.post("/api/set-model")
def set_model(body: ModelSetIn):
    agent_core.MODEL = body.model.strip()
    return {"current": agent_core.MODEL}


@app.post("/api/run-code")
def run_code(body: CodeRunIn):
    """Executes small Python test code with a strict timeout and returns stdout/stderr."""
    code = body.code.strip()
    if not code:
        return {"stdout": "", "stderr": "No code provided", "time_ms": 0}

    # Lightweight safety checks for interactive sandbox
    forbidden = ["import os", "import sys", "import subprocess", "import shutil", "open(", "rmdir", "unlink", "socket"]
    for word in forbidden:
        if word in code:
            return {
                "stdout": "",
                "stderr": f"Restricted: `{word}` is disabled in the practice playground for safety.",
                "time_ms": 0,
            }

    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=body.timeout or 4.0,
        )
        elapsed = round((time.time() - t0) * 1000, 1)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": proc.returncode,
            "time_ms": elapsed,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out (> {body.timeout}s). Check for infinite loops in while/recursion.",
            "exit_code": 124,
            "time_ms": round((time.time() - t0) * 1000, 1),
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1, "time_ms": 0}


class FlashcardGenIn(BaseModel):
    topic: Optional[str] = "general"
    count: Optional[int] = 5


@app.get("/api/flashcards/daily")
def daily_flashcards(date: Optional[str] = None):
    """Returns today's curated set of 5 interview flashcards."""
    return get_daily_flashcards(date_str=date, count=5)


@app.post("/api/flashcards/generate")
def custom_flashcards(body: FlashcardGenIn):
    """Generates fresh AI flashcards on any requested topic."""
    return generate_ai_flashcards(topic=body.topic or "general", count=body.count or 5, model=agent_core.MODEL)

