#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
# Wir gehen davon aus, dass PYTHONPATH auf das Projekt zeigt (..)
export PYTHONPATH=..:${PYTHONPATH:-}
pytest -q --junitxml=reports/pytest_wallet.xml
echo "JUnit Report unter reports/pytest_wallet.xml"
