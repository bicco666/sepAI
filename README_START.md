# Solana Trading Organisation Dashboard - Schnellstart

## 🚀 Dashboard starten

### Automatisches Startscript (empfohlen)

```bash
# Startet Server, öffnet Browser und prüft alle Systeme
python start_dashboard.py
```

### Manuell starten

```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Server starten
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Im Browser öffnen: http://127.0.0.1:8000/
```

## 📋 Was das Startscript macht

1. **Server-Status prüfen**: Verwendet bestehenden Server falls bereits aktiv
2. **Systemdiagnose**: Prüft alle Abteilungen (2-5) und deren Status
3. **Wallet-Status**: Überprüft Solana-Wallet und Netzwerk
4. **Browser öffnen**: Startet automatisch den Standardbrowser
5. **Status-Anzeige**: Zeigt detaillierte Informationen über alle Systeme

## 🏢 Abteilungsstatus (Bereitstellung)

Das Dashboard zeigt den Status folgender Abteilungen:

- **Quality (Abteilung 2)**: Audit, CAPA, Change-Gate
- **Research (Abteilung 3)**: Exploration neuer Ertragsquellen
- **Analysis (Abteilung 4)**: Strategien, Backtests, Runbooks
- **Execution (Abteilung 5)**: Orders, Limits, Circuit Breaker

## 💰 Wallet-Funktionen

- **Netzwerk-Anzeige**: Devnet/Mainnet/Custom-Erkennung
- **Balance-Anzeige**: Live-Kontostand aktualisierung
- **Airdrop-Funktion**: Nur bei Devnet verfügbar
- **Adresse-Management**: Automatische Generierung und Verwaltung

## 🧪 Testfunktionen

- **Bundle-Test**: Vollständige Systemdiagnose
- **Wallet-Tests**: Spezifische Wallet-Funktionsprüfung
- **Agent-Tests**: Abteilungsstatus-Validierung
- **Report-System**: Automatische Fehlerdokumentation

## 📊 Dashboard-Features

- **Live-Updates**: Automatische Datenaktualisierung
- **Responsive Design**: Funktioniert auf Desktop und Mobile
- **Toast-Benachrichtigungen**: User-Feedback für Aktionen
- **Report-Management**: Testberichte speichern und verwalten

## 🔧 Technische Details

- **Backend**: FastAPI mit Uvicorn
- **Frontend**: Vanilla JavaScript mit modernen ES6+ Features
- **Styling**: Responsive CSS mit Dark Theme
- **API**: RESTful Endpunkte für alle Funktionen

## 🎯 Verwendung

1. Script ausführen: `python start_dashboard.py`
2. Warten bis alle Systeme geprüft sind
3. Dashboard öffnet automatisch im Browser
4. Alle Abteilungen sollten "bereit" anzeigen
5. Wallet-Funktionen sind verfügbar

Das Dashboard ist vollständig funktionsfähig und bereit für den Produktiveinsatz!