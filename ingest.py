import pathlib
import re

import chromadb
import ollama

EMBED_MODEL = "nomic-embed-text"

BASE_DIR = pathlib.Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "db")

client = chromadb.PersistentClient(path=DB_PATH)
try:
    client.delete_collection("dsa_notes")  # rebuild from scratch each run
except Exception:
    pass
collection = client.create_collection("dsa_notes")

docs, ids, metas = [], [], []
for path in sorted((BASE_DIR / "notes").rglob("*.md")):
    text = path.read_text().strip()
    title = text.split("\n")[0].lstrip("# ").strip()
    category = path.parent.name if path.parent.name != "notes" else "general"

    sections = re.split(r"\n(?=## )", text)
    # new-style notes: sections[0] is just the title, so skip it
    body_sections = sections[1:] if len(sections) > 1 else sections

    for i, sec in enumerate(body_sections):
        docs.append(f"{title} ({category}): {sec.strip()}")
        ids.append(f"{category}/{path.stem}-{i}")
        metas.append({"source": f"{category}/{path.name}"})

BATCH = 32
for s in range(0, len(docs), BATCH):
    chunk = docs[s:s + BATCH]
    embs = ollama.embed(model=EMBED_MODEL, input=chunk)["embeddings"]
    collection.add(ids=ids[s:s + BATCH], documents=chunk,
                   embeddings=embs, metadatas=metas[s:s + BATCH])

print(f"Indexed {len(docs)} chunks from {len(set(m['source'] for m in metas))} notes.")