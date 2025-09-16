# sepAI – Wallet/API Tests (10 Fälle + Report)

## Voraussetzungen
- Deine API muss im Projekt `sepAI/` im Parent-Verzeichnis liegen.
- Aktiviere deine venv, installiere die Test-Abhängigkeiten:
  ```bash
  pip install -r requirements-tests.txt
  ```

## Ausführen
```bash
# im Ordner sepAI_tests/
export PYTHONPATH=..:$PYTHONPATH
./run_tests.sh
# oder:
pytest -q --junitxml=reports/pytest_wallet.xml
python generate_report.py
```

Der Markdown-Report liegt anschließend unter `reports/wallet_report.md`.

## Test-Scope
1. `/api/v1/wallet/address` erstellt/liest Keypair (Datei).
2. `/api/v1/wallet/health` liefert Status.
3. `/api/v1/wallet/balance` ohne Solana-Deps → 503.
4. `/api/v1/wallet/balance` mit Mock → 200 & korrekter Wert.
5. `/api/v1/wallet/airdrop` mit Mock → 200 & Signature.
6. `/api/v1/wallet/airdrop` Rate-Limit → 429.
7. `/api/v1/wallet/balance` invalid address → 500 (aktuelle Implementation).
8. `/api/v1/agents/research/generate` erzeugt Ideen.
9. `/api/v1/agents/status` enthält alle Departments.
10. `/api/v1/wallet/address` zweimal → gleiche Adresse (Persistenz).

> Hinweis: Die Tests **mocken** Solana-Calls, wo sinnvoll, damit keine echten RPCs erforderlich sind.
