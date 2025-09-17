# Implementierungsanweisung für Coding-LLM (Grok code fast 1)

Diese Datei beschreibt die Schritte, wie das Coding-LLM unser Projekt (Solana/Ethereum Trading Dashboard) umsetzen soll.  
Ziel: **Einfaches lokales System ohne DB und Docker, mit identischen index.html, Tests per Link und Reports unter `reports/`.**

---

## 1. Ordnerstruktur
```
sepAI/
  backend/
    app.py
    state.py
    scheduler.py
    chains/
      solana_mock.py
      ethereum_mock.py
  frontend/
    index.html
    index_alt.html   # identisch (Symlink oder Kopie)
    js/app.js
  tests/
    test_flow_basic.py
    test_chains.py
    test_budget_policy.py
    test_audit.py
    test_dashboard.py
  reports/
  tools/
    sync_index.sh
  README.md
```

---

## 2. API-Endpunkte
- `GET  /healthz`  
- `POST /api/v1/ideas` → neue Idee (state=NEW)  
- `POST /api/v1/ideas/{id}/to-analysis` → state=NEEDS_REVIEW  
- `POST /api/v1/ideas/{id}/schedule` → state=SCHEDULED  
- `POST /api/v1/orders/{id}/execute` → state=CLOSED/FAILED  
- `GET  /api/v1/ideas`, `GET /api/v1/orders`  
- `GET  /api/v1/tests/run?case=1` → führt Testfall 1 aus  
- `GET  /api/v1/tests/bundle` → alle Tests  
- `POST /api/v1/audit/run` → Quality-Audit  

---

## 3. Business-Logik
- **Chain pro Idee:** `chain = "solana" | "ethereum"` → Execution ruft passenden Mock.  
- **Budget-Policy:** `cap = min(0.05*budget_total*p_success, 0.05*budget_total)`  
- **Reports:** Jede Test/Audit-Route schreibt Markdown unter `reports/`.  

---

## 4. Basis-Testfälle
1. **Flow:** Idee → Analyse → Auftrag → Execution.  
2. **Chains:** Solana 0.1, Ethereum 0.001.  
3. **Budget:** >Cap → Fehler, ≤Cap → OK.  
4. **Audit:** End-to-End Testlauf.  
5. **Dashboard:** IDs/Links vorhanden.  
**Bundle:** führt alle obigen Tests zusammen.  

---

## 5. Frontend (index.html)
- Ergänze IDs: `btn-idea`, `btn-to-analysis`, `btn-schedule`, `btn-execute`, `tbl-ideas`, `tbl-orders`, `tbl-history`.  
- Quick Tab „Test“ mit Links zu `/api/v1/tests/run?case=1` und `/api/v1/tests/bundle`.  
- Zweite index.html per Symlink oder `tools/sync_index.sh`.  

---

## 6. Umsetzungsschritte
1. **Backend-Skelett (Flask + state.py)**.  
2. **Ideen/Orders-API (Transitions)**.  
3. **Chains-Mocks + Budget-Policy**.  
4. **Test-Trigger, Bundle, Audit**.  
5. **Frontend-IDs + Test-Links + sync_index.sh**.  

---

## 7. Kurz-Prompts für Coding-LLM
- **A) backend/app.py (Healthz)**  
- **B) backend/state.py (Models + Store)**  
- **C) chains/solana_mock.py, ethereum_mock.py**  
- **D) validate_budget() in state.py**  
- **E) Ideen/Orders-Routen in app.py**  
- **F) Testtrigger/Bundle/Audit in app.py**  
- **G) Tests (5 Dateien)**  
- **H) HTML-IDs + Testlinks in index.html**  
- **I) frontend/js/app.js (fetch)**  
- **J) tools/sync_index.sh**  

---

## 8. Quickstart
```
python -m venv .venv && source .venv/bin/activate
pip install flask flask-cors pytest
python backend/app.py
pytest -q
ls reports/
```

---

## Definition of Done (v1)
- Keine DB/Docker, index.html identisch.  
- Tests per UI-Links triggerbar, Reports unter `reports/`.  
- Alle 5 Basis-Testfälle grün.  
- Audit manuell und periodisch möglich.  
