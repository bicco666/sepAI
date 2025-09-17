# sepAI Patch – Minimaler Systemtest (v1)

Dieser Patch liefert eine **funktionierende Minimal-App**:
- genau **eine** `index.html` (unter `frontend/`), vom Backend ausgeliefert
- Button **„Systemdurchlauf“**: Idee → Analyse → Ausführung → Quality, mit **Report** unter `reports/`
- In-Memory-State, **keine DB, kein Docker**

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

Öffne im Browser: http://localhost:8000

## Buttons
- **Systemdurchlauf**: erzeugt eine Idee, analysiert, plant Auftrag, führt ihn aus, macht Quality-Check, schreibt Report.
- **Kontostand abfragen**: zeigt (mock) Balance.
- **Letzten Report laden**: zeigt Text des jüngsten Reports.

## Struktur
- `backend/app.py` – FastAPI-App, Endpunkte, In-Memory-State.
- `backend/services/reporting.py` – Report-Schreiber (Markdown).
- `frontend/index.html` – **eine** kanonische Seite.
- `frontend/app.js` – einfache Fetch/DOM-Logik.
- `reports/` – generierte Reports.

## Hinweis
Bitte öffne das Dashboard immer über **http://localhost:8000** – so wird garantiert die _eine_ richtige `index.html` geladen.
