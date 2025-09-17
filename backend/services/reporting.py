from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def write_report(name: str, lines: list[str]) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    p = REPORTS_DIR / f"{ts}_{name}.md"
    content = "# " + name + "\n\n" + "\n".join(f"- {line}" for line in lines) + "\n"
    p.write_text(content, encoding="utf-8")
    return str(p)

def latest_report() -> dict:
    files = sorted(REPORTS_DIR.glob("*.md"))
    if not files:
        return {"found": False}
    p = files[-1]
    text = p.read_text(encoding="utf-8")
    ok = "RESULT: OK" in text
    return {"found": True, "path": str(p), "ok": ok, "content": text}
