import xml.etree.ElementTree as ET
from pathlib import Path
import sys, json, datetime

junit = Path("reports/pytest_wallet.xml")
out = Path("reports/wallet_report.md")
if not junit.exists():
    print("JUnit XML nicht gefunden:", junit, file=sys.stderr)
    sys.exit(1)
tree = ET.parse(junit)
root = tree.getroot()

total = int(root.attrib.get("tests", 0))
failures = int(root.attrib.get("failures", 0))
errors = int(root.attrib.get("errors", 0))
skipped = int(root.attrib.get("skipped", 0))
passed = total - failures - errors - skipped

lines = []
lines.append(f"# Wallet/API Testreport")
lines.append("")
lines.append(f"- Datum: {datetime.datetime.now().isoformat(timespec='seconds')}")
lines.append(f"- Gesamt: **{total}**, Passed: **{passed}**, Failed: **{failures}**, Errors: **{errors}**, Skipped: **{skipped}**")
lines.append("")
lines.append("## Details")

for ts in root.findall("testsuite"):
    suite_name = ts.attrib.get("name","suite")
    for tc in ts.findall("testcase"):
        name = tc.attrib.get("name","case")
        classname = tc.attrib.get("classname","")
        status = "PASSED"
        detail = ""
        f = tc.find("failure")
        e = tc.find("error")
        s = tc.find("skipped")
        if f is not None:
            status = "FAILED"
            detail = f.attrib.get("message","") + "\n" + (f.text or "")
        elif e is not None:
            status = "ERROR"
            detail = e.attrib.get("message","") + "\n" + (e.text or "")
        elif s is not None:
            status = "SKIPPED"
            detail = s.attrib.get("message","") or ""
        lines.append(f"- **{name}** ({classname}) → {status}")
        if detail.strip():
            lines.append(f"  ```\n{detail.strip()}\n```")

out.write_text("\n".join(lines), encoding="utf-8")
print("Report geschrieben:", out)
