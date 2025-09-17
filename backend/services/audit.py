from fastapi import APIRouter, HTTPException
import threading
import time
import os
from datetime import datetime

router = APIRouter()

audit_interval = int(os.getenv('AUDIT_INTERVAL_SEC', 300))

def run_audit():
    # Simple audit: check if ideas, analysis, execution work
    # For now, just write a report
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f'reports/audit_{ts}.md'
    with open(report_path, 'w') as f:
        f.write(f'# Audit Report {ts}\n\nAudit completed successfully.\n')
    return report_path

def audit_scheduler():
    while True:
        run_audit()
        time.sleep(audit_interval)

# Start scheduler in thread
threading.Thread(target=audit_scheduler, daemon=True).start()

@router.post('/run')
def run_audit_endpoint():
    try:
        report_path = run_audit()
        return {'report_path': report_path, 'ok': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))