import chromadb
import ollama

MODEL = "llama3.2:3b"
EMBED_MODEL = "nomic-embed-text"

collection = chromadb.PersistentClient(path="db").get_collection("dsa_notes")


# ---------- TOOLS (the model reads these docstrings to decide when to use them) ----------

def search_notes(query: str) -> str:
    """Search the DSA study notes for a topic, technique or concept.

    Args:
        query: What to look up, e.g. "two pointers" or "hashmap".
    """
    q_emb = ollama.embed(model=EMBED_MODEL, input=query)["embeddings"][0]
    res = collection.query(query_embeddings=[q_emb], n_results=3)
    return "\n\n".join(res["documents"][0])


def get_hint(problem: str) -> str:
    """Give the student a short hint for a DSA problem WITHOUT revealing the full solution.
    Use when the student asks for a hint or says they want to solve it themselves.

    Args:
        problem: The full problem statement.
    """
    notes = search_notes(problem)
    resp = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": f"Study notes:\n{notes}\n\nProblem: {problem}\n\n"
                       "Give ONLY a 2-sentence hint: name the pattern or data structure "
                       "and why it fits. No code, no full solution.",
        }],
        options={"temperature": 0.3},
    )
    return resp.message.content


def review_code(code: str) -> str:
    """Review the student's code: find bugs, state time and space complexity,
    and suggest a better approach if there is one.

    Args:
        code: The student's code.
    """
    resp = ollama.chat(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": "Review this code. In short bullets: 1) any bugs, "
                       "2) time and space complexity, 3) a better approach if one exists.\n\n"
                       + code,
        }],
        options={"temperature": 0.3},
    )
    return resp.message.content


TOOLS = {"search_notes": search_notes, "get_hint": get_hint, "review_code": review_code}

SYSTEM_PROMPT = """You are a DSA tutor with three tools.
- Use search_notes when the student asks about a DSA concept or technique.
- Use get_hint when the student asks for a hint for a problem.
- Use review_code when the student shares code.
- For greetings or small talk, answer directly without tools.
After using a tool, answer the student clearly and briefly using the tool result.
Never invent extra requirements for a problem."""


# ---------- AGENT LOOP ----------

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
print("DSA Agent ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    for _ in range(5):  # safety limit so it can never loop forever
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=list(TOOLS.values()),
            options={"temperature": 0.3},
        )
        msg = response.message
        messages.append(msg)

        if not msg.tool_calls:  # no tool needed -> this is the final answer
            print(f"Tutor: {msg.content}\n")
            break

        for call in msg.tool_calls:
            name, args = call.function.name, call.function.arguments
            print(f"  [tool called: {name}({args})]")
            try:
                result = TOOLS[name](**args)
            except Exception as e:
                result = f"Tool error: {e}"
            messages.append({"role": "tool", "content": str(result), "tool_name": name})