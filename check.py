import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent


def step(name, fn):
    try:
        out = fn()
        print(f"OK    {name}: {out}")
    except Exception:
        print(f"FAIL  {name}")
        traceback.print_exc()


def t_ollama():
    import ollama
    return [m.model for m in ollama.list().models]


def t_embed():
    import ollama
    e = ollama.embed(model="nomic-embed-text", input="test")["embeddings"][0]
    return f"{len(e)} numbers"


def t_db():
    import chromadb
    c = chromadb.PersistentClient(path=str(BASE / "db")).get_collection("dsa_notes")
    return f"{c.count()} chunks"


def t_files():
    return {
        "app.py": (BASE / "app.py").exists(),
        "agent_core.py": (BASE / "agent_core.py").exists(),
        "static/index.html": (BASE / "static" / "index.html").exists(),
        "notes folder": (BASE / "notes").exists(),
    }


def t_agent():
    from agent_core import new_session, run_turn_stream
    events = list(run_turn_stream(new_session(), "hi"))
    return events[:3]


step("1 ollama running + models", t_ollama)
step("2 embedding model", t_embed)
step("3 notes database", t_db)
step("4 project files", t_files)
step("5 agent answers 'hi'", t_agent)
print("\nDone. Copy everything above and paste it to me.")