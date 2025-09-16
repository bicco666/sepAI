from fastapi import APIRouter
from typing import Dict, Any
import tempfile, subprocess, json, os, time, sys
from pathlib import Path
import xml.etree.ElementTree as ET

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"
TESTS_DIR = PROJECT_ROOT / "tests" / "api"
REPORTS_DIR.mkdir(exist_ok=True)

def _run_pytest() -> Dict[str, Any]:
    junit = REPORTS_DIR / "pytest_api.xml"
    cmd = [sys.executable, "-m", "pytest", str(TESTS_DIR), "-q", f"--junitxml={junit}"]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH','')}"
    p = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, capture_output=True, text=True, timeout=300)
    out = p.stdout.strip()
    err = p.stderr.strip()
    code = p.returncode

    # Parse JUnit
    totals = {"total": 0, "failures": 0, "errors": 0, "skipped": 0, "passed": 0}
    try:
        tree = ET.parse(junit)
        root = tree.getroot()
        totals["total"] = int(root.attrib.get("tests", 0))
        totals["failures"] = int(root.attrib.get("failures", 0))
        totals["errors"] = int(root.attrib.get("errors", 0))
        totals["skipped"] = int(root.attrib.get("skipped", 0))
        totals["passed"] = totals["total"] - totals["failures"] - totals["errors"] - totals["skipped"]
    except Exception:
        # Keep defaults if parsing fails
        pass

    return {
        "ok": code == 0,
        "code": code,
        "stdout_tail": "\n".join(out.splitlines()[-60:]) if out else "",
        "stderr_tail": "\n".join(err.splitlines()[-60:]) if err else "",
        "junit": str(junit),
        "totals": totals,
        "ts": time.time(),
    }

@router.post("/run")
def run_tests():
    return _run_pytest()
