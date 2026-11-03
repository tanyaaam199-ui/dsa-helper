import chromadb
import ollama

MODEL = "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"

collection = chromadb.PersistentClient(path="db").get_collection("dsa_notes")

SYSTEM_PROMPT = """You are a DSA (data structures and algorithms) tutor.
Answer directly and simply.
- Give the answer first, then a short explanation.
- For a problem: explain the idea in 2-3 sentences, then give Python code, then time and space complexity.
- For a concept: give a simple definition and one small example.
- If study notes are provided, base your answer on them.
- Never reply with a question. Keep it short."""

HINT_RULE = (
    "\n\n[Give ONLY a short hint: name the pattern or data structure to use "
    "and why, in 2 sentences. No code, no full solution.]"
)


def retrieve(question, k=3):
    q_emb = ollama.embed(model=EMBED_MODEL, input=question)["embeddings"][0]
    res = collection.query(query_embeddings=[q_emb], n_results=k)
    return res["documents"][0], res["metadatas"][0]


history = [{"role": "system", "content": SYSTEM_PROMPT}]
print("DSA Tutor ready. '/hint <problem>' for a hint only. 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break
    if not user_input:
        continue

    hint_mode = user_input.startswith("/hint")
    question = user_input[len("/hint"):].strip() if hint_mode else user_input

    # RETRIEVE
    chunks, metas = retrieve(question)
    sources = sorted({m["source"] for m in metas})
    print(f"[notes used: {', '.join(sources)}]")

    # AUGMENT: notes go into this one call only, not into saved history
    context = "\n\n".join(chunks)
    augmented = f"Study notes:\n{context}\n\nStudent: {question}"
    if hint_mode:
        augmented += HINT_RULE

    # GENERATE
    print("Tutor: ", end="", flush=True)
    reply = ""
    for chunk in ollama.chat(
        model=MODEL,
        messages=history + [{"role": "user", "content": augmented}],
        stream=True,
        options={"temperature": 0.3},
    ):
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        reply += piece
    print("\n")

    # history keeps the clean question, so it doesn't bloat with notes
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": reply})
    