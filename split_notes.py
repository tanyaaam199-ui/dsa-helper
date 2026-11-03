import pathlib
import re

raw = pathlib.Path("batch.txt").read_text()
parts = re.split(r"^=== (.+?) ===\s*$", raw, flags=re.M)

count = 0
for name, body in zip(parts[1::2], parts[2::2]):
    out = pathlib.Path("notes") / name.strip()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body.strip() + "\n")
    count += 1

print(f"Wrote {count} notes.")