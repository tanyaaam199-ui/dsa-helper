import json
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

try:
    import chromadb
except Exception:
    chromadb = None

try:
    import ollama
except Exception:
    ollama = None

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# On cloud (Vercel) with GROQ_API_KEY, default to Groq Cloud Llama; otherwise local llama3.2:3b
MODEL = "llama-3.3-70b-versatile" if os.getenv("GROQ_API_KEY") else "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"
OPTIONS = {
    "temperature": 0.2,
    "num_ctx": 2048,           # keep context bounded for snappy local inference on Mac
}

DB_PATH = str(BASE_DIR / "db")

# Singleton ChromaDB client & collection to avoid re-opening DB files on every query
_client = None
_collection = None


def get_collection():
    global _client, _collection
    if chromadb is None:
        return None
    if _collection is None:
        try:
            _client = chromadb.PersistentClient(path=DB_PATH)
            _collection = _client.get_collection("dsa_notes")
        except Exception:
            _collection = None
    return _collection


def reload_collection():
    """Call if notes were re-indexed."""
    global _client, _collection
    if chromadb is None:
        return None
    try:
        _client = chromadb.PersistentClient(path=DB_PATH)
        _collection = _client.get_collection("dsa_notes")
    except Exception:
        _collection = None
    return _collection


def retrieve_fallback_keyword(query, k=3):
    """Zero-dependency keyword retrieval directly from markdown files.
    Works anywhere, including serverless / cloud deployments without ChromaDB or Ollama!"""
    notes_dir = BASE_DIR / "notes"
    if not notes_dir.exists():
        return "", []

    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    if not words:
        return "", []

    scored = []
    for p in sorted(notes_dir.rglob("*.md")):
        try:
            txt = p.read_text(encoding="utf-8")
            txt_lower = txt.lower()
            stem_lower = p.stem.lower()
            # Prioritize title / filename matches heavily
            score = sum(txt_lower.count(w) * (4 if w in stem_lower else 1) for w in words)
            if score > 0:
                rel = str(p.relative_to(notes_dir))
                scored.append((score, txt, rel))
        except Exception:
            continue

    if not scored:
        return "", []

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:k]
    docs = [item[1][:1500] for item in top]
    sources = [item[2] for item in top]
    return "\n\n".join(docs), sources


def retrieve(query, k=3):
    """Attempts vector retrieval via Ollama embeddings; seamlessly falls back to keyword matching."""
    try:
        col = get_collection()
        q_emb = ollama.embed(model=EMBED_MODEL, input=query)["embeddings"][0]
        res = col.query(query_embeddings=[q_emb], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        sources = []
        if metas:
            for m in metas:
                if isinstance(m, dict) and "source" in m:
                    sources.append(m["source"])
        sources = list(dict.fromkeys(sources))
        return "\n\n".join(docs), sources
    except Exception as e:
        # Seamlessly fallback to direct markdown keyword retrieval
        return retrieve_fallback_keyword(query, k=k)


SYSTEM_PROMPT = """You are a precise, friendly DSA tutor.

Facts you must always get right:
- BFS = Breadth-First Search: explores a graph level by level using a queue. "Breadth" means width (not "breath").
- DFS = Depth-First Search: goes as deep as possible first, using recursion or a stack.
- MST = Minimum Spanning Tree. DSU = Disjoint Set Union (Union-Find). DP = Dynamic Programming.

Rules:
- Reference notes are attached to most questions. When they match the question, base your answer on them
  and stay consistent with them. Use correct technical terms.
- Do not use real-world stories or analogies unless the student asks for one.
- If the student says you made a mistake, or asks whether something is right, check carefully.
  If they are right, say so in a few words and give the correct fact. If they are wrong, correct them briefly.
  Never invent an explanation to justify a wrong word or claim.
- Never apologize. Never write "sorry", "I'm sorry", "I apologize", "unfortunately",
  "I couldn't find", "as an AI" or "I don't have access".
- Never mention your notes or your tools.
- No filler openings ("Sure", "Great question", "Certainly") and no closing offers
  ("Let me know if...", "Would you like...").
- Start directly with the answer.
- Follow the length rule given for each message.
- Never invent extra requirements for a problem."""

# ---------- ANSWER LENGTH & MODE RULES ----------

STYLE = {
    "oneline": "Length rule: answer in exactly ONE sentence, at most 25 words. No code, no lists.",
    "brief": "Length rule: keep it SHORT, at most 4 short lines (about 60 words). Lead with the answer. "
             "No code unless the student asked for code.",
    "code": "Length rule: give clean, optimal Python code first, then one line with the time and space complexity. "
            "At most one extra sentence.",
    "review": "Length rule: review the student's code in concise bullets: 1) any bugs / edge cases, "
              "2) time and space complexity, 3) a cleaner/better approach with brief code if applicable. "
              "Be constructive and direct.",
    "hint": "Length rule: give ONLY a 2-sentence hint: name the pattern or data structure and why it fits. "
            "Do NOT reveal the full solution or write complete code. Keep the student thinking.",
    "detailed": "Length rule: explain thoroughly. Give the technical intuition in 1-2 sentences, then a "
                "step-by-step walkthrough, a small worked example, Python code, and the time and space "
                "complexity. No real-world stories.",
    "quiz": "Length rule: give ONE challenging DSA interview practice question or drill on this topic. "
            "Include 4 multiple choice options (A, B, C, D). Do NOT give away the correct answer yet; "
            "ask the student to choose.",
}


def pick_mode(text):
    t = text.lower()
    if re.search(r"\b(quiz|drill|test me|practice question|problem for me)\b", t):
        return "quiz"
    if re.search(r"\b(hint|clue|nudge|guide me without spoiling)\b", t):
        return "hint"
    if re.search(r"\b(one|1|single)[\s-]*(line|liner|sentence)\b|\bin a line\b", t):
        return "oneline"
    if re.search(r"\b(review|debug|bug|bugs|wrong with|fix my|critique|check my code)\b", t) or "def " in t:
        return "review"
    if re.search(r"\b(explain|detail|detailed|elaborate|in depth|step by step|walk me through|deeper|teach me|tell me more|more about)\b", t):
        return "detailed"
    if re.search(r"\b(code|implement|implementation|program|function|solution|solve)\b", t):
        return "code"
    if re.search(r"\b(brief|briefly|short|shortly|in short|tl;?dr|quick|quickly|summary|summarize|nutshell)\b", t):
        return "brief"
    return "brief"


SMALL_TALK = re.compile(
    r"^\s*(hi+|hello+|hey+|yo|thanks|thank you|thx|ok|okay|cool|nice|bye|good (morning|afternoon|evening|night))[\s!.?]*$",
    re.I)


def last_user_text(messages):
    for m in reversed(messages):
        if isinstance(m, dict) and m.get("role") == "user":
            return m["content"]
    return ""


def styled(messages, mode, notes=""):
    """Adds the length rule and the notes as the last message of this call only (not saved in history)."""
    extra = STYLE.get(mode, STYLE["brief"])
    if notes:
        extra += ("\n\nReference notes (use them as the source of truth when they match the question; "
                  "do not mention them):\n" + notes)
    return messages + [{"role": "system", "content": extra}]


# ---------- REMOVE APOLOGIES / FILLER AT THE START OF AN ANSWER ----------

ROLE = re.compile(r"^\s*assistant\s*:?[ \t]*\n+", re.I)
APOLOGY = re.compile(
    r"^\s*(?:(?:i'?m|i am|we are|we're)\s+(?:really\s+|so\s+|very\s+)?sorry|sorry|i apologi[sz]e|my apologies)"
    r"\b[^.!?\n]*[.!?]?\s*", re.I)
OPENER = re.compile(
    r"^\s*(?:unfortunately|great question|sure thing|sure|certainly|of course|absolutely|okay|ok)\b\s*[,!.:]?\s*", re.I)


def clean_start(s):
    prev = None
    while prev != s:
        prev = s
        s = ROLE.sub("", s, count=1)
        s = APOLOGY.sub("", s, count=1)
        s = OPENER.sub("", s, count=1)
    return s[:1].upper() + s[1:]


def stream_clean(pieces):
    """Holds back the first ~35 characters (or first newline), cleans them, then streams smoothly."""
    buf, started = "", False
    for piece in pieces:
        if started:
            yield piece
            continue
        buf += piece
        if len(buf) >= 35 or "\n" in buf:
            started = True
            yield clean_start(buf)
    if not started and buf:
        yield clean_start(buf)


# ---------- GROQ CLOUD LLAMA INFERENCE ----------

def is_groq_model(model_name: str) -> bool:
    m = model_name.lower()
    return (
        "groq" in m
        or "llama-3.3" in m
        or "llama-3.1" in m
        or (bool(os.getenv("GROQ_API_KEY")) and m.startswith("llama-3"))
    )


def clean_model_name(model_name: str) -> str:
    """Extracts raw model id from UI label (e.g. 'llama-3.3-70b-versatile (Groq Cloud)' -> 'llama-3.3-70b-versatile')."""
    return model_name.split()[0].strip()


def stream_groq_chat(messages, model: str):
    """Streams completions from Groq Cloud running Meta's Llama 3 models at 300+ tokens/sec."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Get a free API key at https://console.groq.com and save it in your settings or .env file."
        )

    clean_model = clean_model_name(model)
    if not clean_model or clean_model == "llama3.2:3b":
        clean_model = "llama-3.3-70b-versatile"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": clean_model,
        "messages": messages,
        "temperature": 0.2,
        "stream": True,
        "max_tokens": 2048
    }

    with httpx.Client(timeout=30.0) as client:
        with client.stream("POST", url, headers=headers, json=payload) as response:
            if response.status_code != 200:
                err_text = response.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"Groq API error ({response.status_code}): {err_text}")

            for line in response.iter_lines():
                if not line:
                    continue
                line = line.strip()
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except Exception:
                        continue


# ---------- AGENT TURN ----------

def new_session():
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def run_turn_stream(messages, user_text, mode_override=None, model_override=None):
    """Runs one user message through the agent and yields events for the website in a single streaming pass."""
    mode = mode_override if (mode_override and mode_override in STYLE) else pick_mode(user_text)
    active_model = model_override or MODEL
    prev = last_user_text(messages)
    messages.append({"role": "user", "content": user_text})
    text = ""
    finished = False

    try:
        # Retrieve notes when applicable
        notes = ""
        sources = []
        if not SMALL_TALK.match(user_text) and mode not in ("review",):
            query = user_text
            if len(user_text.split()) < 6 and prev:
                query = prev[:200] + " " + user_text
            notes, sources = retrieve(query)

        # Emit mode & sources info to UI
        yield {"type": "meta", "mode": mode, "model": active_model, "sources": sources}

        styled_msgs = styled(messages, mode, notes)

        # Choose inference engine: Groq Cloud Llama or Local Ollama Llama
        has_groq_key = bool(os.getenv("GROQ_API_KEY", "").strip())

        if is_groq_model(active_model):
            if has_groq_key:
                pieces = stream_groq_chat(styled_msgs, active_model)
            elif ollama is not None:
                # User selected a Groq Cloud model without setting an API key; fallback to local Ollama
                try:
                    stream = ollama.chat(
                        model="llama3.2:3b",
                        messages=styled_msgs,
                        stream=True,
                        options=OPTIONS,
                    )
                    pieces = (c.message.content for c in stream if c.message and c.message.content)
                except Exception:
                    raise ValueError(
                        "GROQ_API_KEY is not set. Get a free API key at https://console.groq.com and save it in your Vercel Environment Variables or .env file."
                    )
            else:
                raise ValueError(
                    "GROQ_API_KEY is not set. Get a free API key at https://console.groq.com and save it in your Vercel Environment Variables or .env file."
                )
        else:
            if ollama is not None:
                try:
                    stream = ollama.chat(
                        model=clean_model_name(active_model),
                        messages=styled_msgs,
                        stream=True,
                        options=OPTIONS,
                    )
                    pieces = (c.message.content for c in stream if c.message and c.message.content)
                except Exception:
                    if has_groq_key:
                        yield {"type": "token", "text": "[Ollama unreachable, routing to Groq Cloud Llama...]\n\n"}
                        pieces = stream_groq_chat(styled_msgs, "llama-3.3-70b-versatile")
                    else:
                        raise ValueError(
                            "Local Ollama is not running or unreachable on this server. "
                            "Please add GROQ_API_KEY to your Vercel Environment Variables to power cloud inference."
                        )
            elif has_groq_key:
                pieces = stream_groq_chat(styled_msgs, "llama-3.3-70b-versatile")
            else:
                raise ValueError(
                    "GROQ_API_KEY is not configured on this server. "
                    "Please add GROQ_API_KEY to your Vercel Project Settings > Environment Variables."
                )

        for piece in stream_clean(pieces):
            text += piece
            yield {"type": "token", "text": piece}

        messages.append({"role": "assistant", "content": text})
        finished = True
        yield {"type": "done"}

    except Exception as e:
        yield {"type": "error", "text": str(e)}

    finally:
        if not finished:
            messages.append({"role": "assistant", "content": (text + " [interrupted]").strip()})
