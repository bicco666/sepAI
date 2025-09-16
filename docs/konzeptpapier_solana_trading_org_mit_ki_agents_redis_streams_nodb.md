# Konzeptpapier – Solana Trading Organisation mit KI‑Agents (v0.1)

*Stand: 15.09.2025 – Autor: Projektteam*

---

## 0) Executive Summary
Ziel ist der Aufbau einer modularen, KI‑gestützten Trading‑Organisation auf der Solana‑Blockchain. Vier wertschöpfende Abteilungen (Forschung, Analyse, Execution, Quality) werden als autonome AI‑Agents betrieben; ein **Update‑Handler** koordiniert Änderungen (SemVer), und die **Geschäftsführung (CEO)** steuert über ein Web‑Dashboard. Primäres Unternehmensziel: *„Mit einem Solana‑Investment das Budget kontinuierlich vermehren.“*

Das Konzept beschreibt **Organisation**, **Architektur**, **Domänenmodelle**, **APIs**, **Workflows/State‑Maschinen**, **UI‑Spezifikation** und **Governance/KPIs** so präzise, dass daraus Implementierung, Tests und Betrieb abgeleitet werden können.

---

## 1) Unternehmensziel & Scope
- **Ziel:** Budgetvermehrung durch Solana‑basierte Investments/Trades (Spot & ausgewählte Tokens auf Solana‑DEXes). 
- **Minimalanforderung Execution:** Zuverlässiges Kaufen/Verkaufen von SOL und ausgewählten Solana‑Tokens; mittelfristig einfache Analyse‑Tasks übernehmen (Graceful Degradation).
- **Analyse:** Marktanalyse (Preis/On‑chain), Strategie‑Dossiers & Runbooks für Execution.
- **Forschung:** Identifikation weiterer Ertragsquellen (DeFi‑Yields, Perps, Airdrops, Staking) innerhalb eines Research‑Budgets.
- **Quality:** Effizienztests, Unit‑/Policy‑Checks, CAPA, Freigaben.
- **Update‑Handler:** Versionierung/Koordination von Script‑/Agent‑Updates (SemVer), Rollout‑Wellen, Rollback.
- **Nicht‑Ziele (v1):** Keine Derivate außerhalb Solana, kein Hochfrequenzhandel, kein Fremdleister‑Kreditrisiko‑Engine.

---

## 2) Organisationsstruktur

```
                       ┌────────────────────┐
                       │   1. Geschäfts-    │
                       │   führung (CEO)    │
                       └───────────┬────────┘
                                   │
        ┌──────────────┬───────────┼───────────────┬──────────────┐
        │              │           │               │              │
 ┌──────┴─────┐ ┌──────┴─────┐ ┌───┴─────┐ ┌───────┴──────┐ ┌─────┴─────┐
 │ 2. Quality │ │ 3. Forschung│ │4. Analyse│ │5. Execution │ │6. Update  │
 │   (Agent)  │ │   (Agent)   │ │  (Agent) │ │   (Agent)   │ │  Handler  │
 └────────────┘ └─────────────┘ └──────────┘ └─────────────┘ └──────────┘
```

**RACI (Kurz):** Forschung (R) Ideen • Analyse (A) Strategien • Quality (C) Gate • Execution (R) Umsetzung • Update‑Handler (C) Release • CEO (I/A) bei roten Risiken.

---

## 3) Agenten (Rollen, I/O, KPIs, SemVer)

## Agentenkommunikation über Redis Streams

Alle Agenten kommunizieren über einen zentralen Message-Bus basierend auf **Redis Streams**. Dies ermöglicht eine asynchrone, entkoppelte und eventbasierte Verarbeitung von Ideen, Strategien und QA-Ergebnissen.

### Vorteile
- Entkoppelte Agentenlogik
- Kollaborative Verarbeitung von Nachrichten
- Persistente Nachrichtenverarbeitung
- Skalierbar und lokal ausführbar

### Beispiel-Streams
- `idea_stream`: neue Ideen von Forschung
- `strategy_stream`: Strategien von Analyse
- `qa_stream`: QA-Ergebnisse von Quality
- `execution_stream`: Ausführungsaufträge

### Beispiel-Nachricht (idea_stream)
```json
{
  "idea_id": "20250915_001",
  "source": "research",
  "asset": "SOL",
  "type": "yield",
  "risk": 3,
  "budget": 0.5
}
```

Jeder Agent abonniert relevante Streams und verarbeitet Nachrichten gemäß seiner Rolle.

Alle produktiven Agents tragen eine **Software‑Version (SemVer)**, initial **v1.2.3**. Jeder Release erhöht Patch/Minor/Major gemäß Change‑Impact. 

### 3.1 Quality‑Agent
**Zweck:** Effizienz & Konformität. **Eingaben:** Logs, Dossiers, Metrics. **Ausgaben:** Audit‑Report, CAPA, Freigabe/Block.  
**Kernaufgaben:**
- Pre‑Trade‑Checks (Budget ≤ Cap, Slippage‑Limit, Exit‑Regel, Zeitfenster gesetzt).  
- Post‑Trade‑Validierung (PnL‑Rekons, Limitverletzungen=0, vollständige Logs).  
- Change‑Gate mit Update‑Handler; kann Releases blockieren.  
**KPIs:** Audit‑Passrate ≥95 %, 0 kritische Risk‑Breaches, MTTR < 1 h.

### 3.2 Forschungs‑Agent
**Zweck:** Ideen‑Generierung (DeFi‑Yields, Staking, Perps, Airdrops, neue Tokens).  
**RISK‑Variable:** Skala 1…5 (1 konservativ, 5 aggressiv) → beeinflusst Priorisierung & Pilot‑Sizing.  
**Outputs:** Research‑Briefs (1‑Pager), Hypothesen‑Backlog, Pilot‑Ergebnisse, Go/No‑Go.  
**KPIs:** ≥3 validierte Ideen/Monat, Budget‑Disziplin 100 %.

### 3.3 Analyse‑Agent
**Zweck:** Strategien erstellen & validieren.  
**RISK‑Variable:** Skala 1…5 → steuert Positionsgröße, Stop‑Distanz, Max‑DD.  
**Outputs:** Strategie‑Dossiers (Entry/Exit, Limits, Parametrik), Runbooks, Risiko‑Szenarien.  
**KPIs:** Out‑of‑Sample‑Treffer, Drawdown innerhalb RISK‑Limits, Forecast‑Brier.

### 3.4 Execution‑Agent
**Zweck:** Disziplinierte Ausführung (Buy/Sell, Order‑Routing, Limits).  
**Minimalfunktion:** SOL & ausgewählte Tokens zuverlässig kaufen/verkaufen (Venue‑Health beachten).  
**KPIs:** Tracking‑Error (Umsetzungstreue), Slippage vs Benchmark, Uptime, Risk‑Breaches=0.

### 3.5 Update‑Handler
**Zweck:** Release‑Koordination, Kompatibilitätstests, Rollback‑Pläne, Change‑Log.  
**Schnittstellen:** Quality‑Gate vor Rollout; Version verteilt/verifiziert; Canary‑Waves.

---

## 4) RISK‑Modell
- **Global:** Dashboard‑Slider für Forschung & Analyse (RISK=1…5).  
- **Pro Idee:** RISK‑Override (1…5) auf Ideenliste.  
- **RISK‑Mapping (v1):**
  - RISK 1→5 ↦ Ziel‑Max‑DD [%] = {4, 6, 8, 10, 12};
  - ↦ Stop‑Distanz [ATR] = {1.0, 1.5, 2.0, 2.5, 3.0};
  - ↦ Positionsgröße [% Budget] = {1, 2, 3, 4, 5}.  
- **Policy:** Idee wird nur **APPROVED**, wenn (`RISK_idee ≤ RISK_global`) und alle Quality‑Checks bestehen (Ausnahme: CEO‑Override).

---

## 6) APIs (REST, v1)
Basis: `/api/v1` (FastAPI). Auth: API‑Key + optional JWT (CEO).

**Wallet**
- `GET /wallet/balance?address=...` → `{balance_sol, ts}`

**Ideas**
- `GET /ideas?limit=20&order=desc`
- `POST /ideas` (body: IdeaDraft) → NEW
- `POST /ideas/{id}/review` → NEEDS_REVIEW → erzeugt Strategy(DRAFT)
- `POST /ideas/{id}/qa` → READY_FOR_QA → QA_REPORT
- `POST /ideas/{id}/approve` → APPROVED
- `POST /ideas/{id}/schedule` (body: {start_at}) → SCHEDULED
- `POST /ideas/{id}/cancel`

**Strategies**
- `GET /strategies/{id}`
- `POST /strategies/{id}/approve`

**Trades**
- `GET /trades?limit=20&order=desc`
- `POST /trades/execute` (body: StrategyRef) → Execution

**Agents**
- `GET /agents`
- `POST /agents/{id}/unit_test`
- `POST /agents/{id}/version/bump` (body: {level: patch|minor|major})

**Releases** (Update‑Handler)
- `POST /releases` (body: {targets, version, notes})
- `POST /releases/{id}/deploy` (canary=true|false)
- `POST /releases/{id}/rollback`

---

## 7) Workflows & State‑Maschine

### 7.1 Ideen‑Pipeline
`NEW → NEEDS_REVIEW → READY_FOR_QA → APPROVED → SCHEDULED → (TRADE) → DONE`
- **NEW:** Forschung erstellt Entwurf (inkl. RISK‑Vorschlag, TTL).  
- **NEEDS_REVIEW:** Analyse erzeugt Strategie‑Dossier (DRAFT).  
- **READY_FOR_QA:** Quality führt Pre‑Trade‑Unit‑ & Policy‑Checks aus.  
- **APPROVED:** Alle Checks OK (oder CEO‑Override).  
- **SCHEDULED:** Execution reserviert Budget/Zeitfenster.  
- **CANCELLED/BLOCKED:** TTL verstrichen, Policy‑Verstoß, Ressourcen‑Konflikt.

### 7.2 Trade‑Lifecycle
`SCHEDULED → OPEN → CLOSED|FAILED` (Duration & PnL werden getrackt)

### 7.3 Release‑Flow (Update‑Handler)
`DRAFT → QA → CANARY → ROLLOUT → VERIFIED` (Rollback‑Pfade definiert)

---

## 8) UI/Dashboard‑Spezifikation (Design‑Stand v0.6)
**Module:**
1. ASCII‑Organigramm (read‑only)  
2. Wallet‑Panel: Adresse, **Kontostand abrufen** (RPC später), Budget/Testbudget  
3. Abteilungen 2–5: Status‑Badges, **Version‑Chip (v1.2.3)**, RISK‑Slider (Forschung/Analyse), **Idee generieren** (Zeitwert + Einheit)  
4. **Zukünftige Aufträge (Ideen)**: Tabelle, neueste zuerst, **RISK‑Override** per Idee, Aktionen (Zur Strategie, Quality‑Check, Einplanen, Verwerfen)  
5. **Historie (20)**: Zeit, Abteilung, Asset, Aktion, Menge, PNL (SOL), Dauer, Status

**Interaktionsprinzipien:** Buttons sind im Design vorhanden; Funktionalität wird erst nach API‑Implementierung aktiviert. Persistenz der RISK‑Werte via localStorage (v1), später Server‑State.

---

## 9) Security & Compliance
- **Keys & RPC:** Secure Secret Store; Roll‑Keys; minimaler Scope.  
- **Order‑Sicherheit:** Circuit‑Breaker, Not‑Aus, Venue‑Health‑Checks.  
- **Ratenbegrenzung:** API Rate‑Limits; Exponential Backoff.  
- **Audit:** Unveränderliche **AUDIT_LOG**; Signatur/Hash.

---

## 10) Observability
- **Metriken:** PnL (SOL), Sharpe, Max‑DD, Hit‑Rate, Slippage, Tracking‑Error; Lead/ Cycle‑Time für Ideen.  
- **Logs:** Strukturierte JSON‑Logs; Korrelation per `trace_id`.  
- **Alarme:** Red‑Flag bei Limitverletzung, QA‑NOK, RPC‑Fehler, HFT‑Anomalien.

---

## 11) Teststrategie
- **Unit‑Tests:**
  - Ideen‑Schema‑Validierung (Budget ≤ Cap, RISK 1..5, TTL gesetzt)
  - Strategy‑Dossier‑Vollständigkeit (Entry/Exit, Stops, Max‑DD)
  - Wallet‑Adapter‑Mock (Balance‑Abruf)
- **Integrationstests:**
  - Ideen→Strategie→QA→SCHEDULED End‑to‑End (Paper‑Trading)
  - Execution‑Adapter (Order‑Lifecycle mit Mock‑Venue)
- **Spezial‑Szenario (Smoke):** 0,1 SOL PUMP‑Token, Haltedauer 1 Minute, Zeit‑Exit, vollständige Logs.

**Akzeptanzkriterien (Beispiele):**
- QA blockiert Execution bei fehlender Exit‑Regel oder überschrittenem Budget.
- Historie zeigt innerhalb 5 s nach Trade‑Abschluss PnL & Dauer.

---

## 12) Architektur & Deployment
- **Backend:** FastAPI (Python), uvicorn, REST+WebSocket.  
- **Agents:** Worker‑Prozesse (Celery/Arq/Async), getrennte Queues pro Abteilung.  
- **Cache/Queue:** Redis.  
- **Docker:** Multi‑Service Compose (api, workers, db, redis, frontend).  
- **CI/CD:** Build, Tests, Security‑Scan, Staging, Canary, Rollout.  
- **Infra:** Cloud VM/K8s (später), TLS, Observability‑Stack (OpenTelemetry, Prometheus/Grafana oder SaaS).

---

## 13) Roadmap (Milestones)
- **M1 – Foundations (2–3 Wochen):** Repo‑Setup, Domainmodelle, API‑Skeleton, Dashboard‑Static, Wallet‑Balance (RPC), Paper‑Trade‑Adapter.  
- **M2 – Ideen‑Pipeline (2–4 Wochen):** Ideen‑CRUD, RISK‑Mapping, Analyse‑Dossiers, QA‑Gate, Scheduling.  
- **M3 – Execution v1 (2–3 Wochen):** SOL/Token Buy/Sell, Limits/Stops, Historie‑Feed.  
- **M4 – Qualität & Updates (2 Wochen):** CAPA, Audit‑Trails, Update‑Handler Releases/Rollback.  
- **M5 – Hardening (fortlaufend):** Sicherheit, Monitoring, Canary‑Rollouts.

---

## 14) Offene Entscheidungen
1. Zulässige DEX‑Venues (Serum‑Forks/Orcas etc.) & Liquiditäts‑Schwellen.  
2. RPC‑Provider (z. B. Helius, QuickNode) und Budget‑Limits.  
3. Default‑TTL für Ideen (z. B. 90 min) & Auto‑Cancel‑Policy.  
4. Exakte RISK‑Mappings (Tabellen‑Feintuning).  
5. Persistenz der RISK‑Overrides (Client vs Server) ab v1.

---

## 15) Anhänge
- **Begriffe & Abkürzungen**
- **Beispiel‑JSON** für IDEA/STRATEGY/QA_REPORT/TRADE
- **Checklisten** (QA‑Gate v1)

> **Version:** v0.1 (Initiale Fassung für Architektur‑ und Implementierungsstart)
