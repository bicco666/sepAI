# sepAI – Erweiterte Tests (Fokus: Solana-Service-Verfügbarkeit)

Diese Tests ergänzen die erste Suite und fokussieren auf das aktuelle Problem:
**Endpunkte müssen sauber reagieren, wenn `solana`-Bibliotheken fehlen**.

## Ausführen
```bash
# im Ordner sepAI_tests_v2/
pip install fastapi uvicorn httpx pytest
export PYTHONPATH=..:$PYTHONPATH
pytest -q --maxfail=3
```

## Abgedeckt
- 503 für Balance/Airdrop, wenn `solana` fehlt (graceful).
- Health meldet `solana_deps: missing(...)`.
- Happy Path via Mocks (Balance/Airdrop OK).
- Rate-Limit → 429, interne Fehler → 500.
- `SOLANA_RPC` liest ENV.
- Address-Erzeugung & Persistenz.
- Ideen-Pipeline (Agents→Ideas).

> Sobald diese Tests grün sind, wissen wir, dass **dein Backend korrekt degradiert**,
> solange die `solana`-Libs fehlen – und bei vorhandenen Libs sauber funktioniert.
