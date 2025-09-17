# Solana/Ethereum Trading Dashboard

Einfaches lokales System für Trading-Ideen und Order-Management ohne Datenbank.

## Quickstart

```bash
# Virtual Environment erstellen und aktivieren
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install flask flask-cors pytest

# Server starten
python backend/app.py

# Tests ausführen
pytest -q

# Reports anzeigen
ls reports/
```

## Architektur

```
sepAI/
├── backend/
│   ├── app.py              # Flask API Server
│   ├── state.py            # In-Memory State Management
│   ├── scheduler.py        # Background Order Processing
│   └── chains/
│       ├── solana_mock.py  # Solana Chain Mock
│       └── ethereum_mock.py # Ethereum Chain Mock
├── frontend/
│   ├── index.html          # Haupt-Dashboard
│   ├── index_alt.html      # Identische Kopie
│   └── js/
│       └── app.js          # Frontend JavaScript
├── tests/                  # Test Cases
├── reports/                # Generated Reports
└── tools/
    └── sync_index.sh       # HTML Sync Script
```

## API Endpunkte

- `GET  /healthz` - Health Check
- `POST /api/v1/ideas` - Neue Idee erstellen
- `GET  /api/v1/ideas` - Ideen auflisten
- `POST /api/v1/ideas/{id}/to-analysis` - Idee zur Analyse
- `POST /api/v1/ideas/{id}/schedule` - Idee einplanen
- `GET  /api/v1/orders` - Orders auflisten
- `POST /api/v1/orders/{id}/execute` - Order ausführen
- `GET  /api/v1/tests/run?case=1` - Einzeltest ausführen
- `GET  /api/v1/tests/bundle` - Alle Tests ausführen
- `POST /api/v1/audit/run` - Quality Audit

## Business Logic

- **Chain Assignment**: Jede Idee hat eine Chain (solana/ethereum)
- **Budget Policy**: `cap = min(0.05*budget_total*p_success, 0.05*budget_total)`
- **State Machine**: NEW → NEEDS_REVIEW → SCHEDULED → CLOSED/FAILED
- **Background Processing**: Scheduler führt geplante Orders automatisch aus

## Test Cases

1. **Flow**: Idee → Analyse → Order → Execution
2. **Chains**: Solana/Ethereum Validierung
3. **Budget**: Policy-Validierung
4. **Audit**: Vollständige Systemprüfung
5. **Dashboard**: UI-Integration

## Reports

Alle Tests und Audits generieren Markdown-Berichte in `reports/`:

```
reports/
├── bundle_test_20231201_120000.md
├── audit_20231201_120000.md
└── ...
