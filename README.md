# Arla RoW DS — Order Intake & Validation Platform

> **6. semester eksamen** · Design og Implementering af Digitale Løsninger · Gruppe 10 · Erhvervsakademi København

Et teknisk MVP der demonstrerer en domænedrevet, cloud-native ordrehåndteringsløsning for Arla Foods Rest of World Distributor Sales. Løsningen modtager ordrer via REST API, validerer dem mod distributøraftaler, persisterer dem struktureret i PostgreSQL og videresender validerede ordrer til SAP. Strukturerede ordredata eksponeres til Power BI via direkte databaseforbindelse.

---

## Indhold

- [Problemstilling](#problemstilling)
- [Arkitektur](#arkitektur)
- [DDD i koden](#ddd-i-koden)
- [Tech stack](#tech-stack)
- [Kom i gang](#kom-i-gang)
- [API-dokumentation](#api-dokumentation)
- [Test](#test)
- [CI/CD og DevSecOps](#cicd-og-devsecops)
- [Observability: Prometheus + Grafana](#observability-prometheus--grafana)
- [Power BI](#power-bi)
- [Projektstruktur](#projektstruktur)

---

## Problemstilling

Arla RoW DS håndterer i dag ordrer manuelt via email, WhatsApp, Teams og Excel i en delt Excel-fil med 85+ ark og ca. 8.600 COGS-rækker. Løsningen er ikke skalerbar, fejlbehæftet og personafhængig.

Dette MVP demonstrerer det centrale ordredomæne som en teknisk front-end der:

- **Modtager** ustrukturerede ordrer via REST API fra alle kanaler
- **Validerer** mod distributøraftaler via Anti-Corruption Layer
- **Persisterer** strukturerede ordredata som single source of truth
- **Videresender** validerede ordrer til SAP (mocket i MVP)
- **Eksponerer** ordredata til Power BI til forecasting og ledelsesrapportering

---

## Arkitektur

Løsningen er bygget med **Hexagonal Architecture (Ports & Adapters)** og **Domain-Driven Design** og består af to selvstændige services (to bounded contexts):

```
Distributør  (EMAIL / WHATSAPP / TEAMS / SMS / API)
    │
    │  POST /orders
    ▼
┌─────────────────────┐     ACL (HTTP)      ┌──────────────────────┐
│    Order Service    │ ──────────────────▶ │   Contract Service   │
│   (Order Context)   │   validér ordre     │  (Contract Context)  │
│                     │ ◀────────────────── │                      │
│  domain/            │   pris + enhed      │  domain/             │
│  ├── aggregates/    │                     │  ├── aggregates/     │
│  ├── events/        │                     │  ├── entities/       │
│  ├── services/      │                     │  └── value_objects/  │
│  └── value_objects/ │                     │                      │
│  infrastructure/    │                     │  infrastructure/     │
│  ├── acl/           │                     │  └── repositories/   │
│  ├── repositories/  │                     │                      │
│  └── sap/           │                     └──────────────────────┘
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│                  PostgreSQL                   │
│              (arla_row database)              │
└──────────────────────────────────────────────┘
           │                        ▲
           │  validerede ordrer     │  Power BI
           ▼                        │  (direkte PostgreSQL-forbindelse)
   ┌───────────────┐
   │  SAP (mock)   │
   └───────────────┘
```

### Bounded Contexts

| Context | Service | Ansvar |
|---|---|---|
| **Order Context** | `order_service` (`:8000`) | Ordremodtagelse, validering, persistering, SAP-integration og forecast |
| **Contract Context** | `contract_service` (`:8001`) | Distributøraftaler, priser, enhedsregler og valideringslogik |

Order Service kalder Contract Service udelukkende via et **Anti-Corruption Layer** (`order_service/app/infrastructure/acl/contract_client.py`), der oversætter Contract Service's svar til Order-domænets sprog og beskytter kernedomænet mod ændringer i kontraktmodellen.

### Ordrelivscyklus

```
IncomingOrder (RECEIVED)
       │
       ▼
OrderValidationService ──── ContractClient (ACL) ──── Contract Service
       │
       ├── Regel 1: Er produktet tilladt i aftalen?
       ├── Regel 2: Er samlet mængde ≥ minimum?
       ├── Regel 3: Matcher enheden aftalens allowed_unit?
       │
       ├── [VALIDATED] ──▶ SAP (mock) ──▶ FORWARDED_TO_SAP
       └── [REJECTED]  ──▶ rejection_reason persisteret
```

---

## DDD i koden

Løsningen følger Khononov (2021) *Learning Domain-Driven Design* med tydelig adskillelse af domænelag, applikationslag og infrastrukturlag (Hexagonal Architecture, kap. 8).

| DDD-byggeklods | Implementering |
|---|---|
| **Aggregate Root** | `Order` · `DistributorContract` |
| **Entity** | `OrderLine` · `Distributor` · `ContractLine` |
| **Value Object** | `OrderStatus` · `Channel` · `Quantity` · `ContractTerms` · `PricingTier` · `MarketRegion` |
| **Domain Service** | `OrderValidationService` · `DemandForecastService` |
| **Domain Event** | `OrderReceived` · `OrderValidated` · `OrderRejected` |
| **Repository** | `OrderRepository` · `ContractRepository` |
| **ACL** | `ContractClient` — beskytter Order Context mod Contract Context |
| **Port** | `OrderRepository`-interface defineret i domænet, implementeret i infrastruktur |

### Centrale designbeslutninger

**IncomingOrder → Order:** En ordre er ikke en `Order` før den er valideret. Overgangen håndhæves af aggregatets `validate()` og `reject()`-metoder — status kan aldrig sættes direkte udefra.

**Unit-validering:** `ContractLine` definerer `allowed_unit` per produkt (`"liters"` for mælk, `"grams"` for ost/smør). `OrderValidationService` afviser ordrer der bruger forkert enhed.

**DemandForecastService i domænelaget:** Servicen opererer udelukkende på domænedata (ordrer) og producerer domænerelevante resultater (forecast per distributør og produkt). Infrastrukturens ansvar er at levere historiske ordrer — servicen kender ikke til databasen.

---

## Tech Stack

| Komponent | Teknologi | Rolle |
|---|---|---|
| **REST API** | FastAPI (Python 3.12) | Application layer — thin by design |
| **Database** | PostgreSQL 16 + SQLAlchemy | Persistering af ordrer og kontrakter |
| **Analytics** | scikit-learn (LinearRegression) | Predictiv analyse i domain service |
| **Containerisering** | Docker + docker-compose | Isoleret kørsel af alle services |
| **CI/CD** | GitHub Actions | Automatisk test og build ved push til main |
| **Observability** | Prometheus + Grafana | Metrics og live dashboard |
| **BI** | Power BI Desktop | Ledelsesrapportering og forecasting |
| **API-test** | Postman | Manuel test og forretningsflow-verifikation |
| **Versionsstyring** | GitHub | Kildekode og branching-strategi |

---

## Kom i gang

### Forudsætninger

- Docker og docker-compose installeret
- Klon repoet:

```bash
git clone https://github.com/Gruppe-10-eksamen/Eksamen_gruppe10.git
cd Eksamen_gruppe10/arla-row-ds
```

### 1. Klargør miljøvariabler

```bash
cp .env.example .env
```

Standardværdierne er sat til lokal udvikling og virker ud af boksen.

### 2. Start hele stacken

```bash
docker-compose up --build
```

Starter: PostgreSQL · Contract Service (`:8001`) · Order Service (`:8000`) · Prometheus (`:9090`) · Grafana (`:3000`)

### 3. Seed kontraktdata

I et nyt terminalvindue:

```bash
docker-compose exec contract-service python -m app.seed
```

Opretter 2 distributøraftaler med 3 produkter hver:

| Produkt | Kode | Enhed |
|---|---|---|
| Arla Milk 1L | `ARLA-MILK-1L` | liters |
| Arla Butter 250g | `ARLA-BUTTER-250G` | grams |
| Puck Cheese 200g | `PUCK-CHEESE-200G` | grams |

### 4. Åbn API-dokumentation

| Service | URL |
|---|---|
| Order Service (Swagger) | http://localhost:8000/docs |
| Contract Service (Swagger) | http://localhost:8001/docs |
| Prometheus targets | http://localhost:9090/targets |
| Grafana dashboard | http://localhost:3000 (admin/admin) |

---

## API-dokumentation

### Opret en ordre (happy path)

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-order-key" \
  -d '{
    "distributor_id": "DIST-001",
    "channel": "EMAIL",
    "order_date": "2026-02-01",
    "lines": [
      {"product_code": "ARLA-MILK-1L", "quantity": 60, "unit": "liters"},
      {"product_code": "PUCK-CHEESE-200G", "quantity": 100, "unit": "grams"}
    ]
  }'
```

**Svar (200):** Status `FORWARDED_TO_SAP` — ordren er valideret og sendt til SAP.

### Afvist ordre (unhappy path — forkert enhed)

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-order-key" \
  -d '{
    "distributor_id": "DIST-001",
    "channel": "WHATSAPP",
    "order_date": "2026-02-01",
    "lines": [
      {"product_code": "ARLA-MILK-1L", "quantity": 60, "unit": "grams"}
    ]
  }'
```

**Svar (200):** Status `REJECTED` med `rejection_reason: "Forkert enhed for ARLA-MILK-1L: ordre bruger 'grams', aftalen kræver 'liters'"`

### Forecast per distributør

```bash
curl http://localhost:8000/forecast/DIST-001 \
  -H "X-API-Key: dev-order-key"
```

Returnerer deskriptiv, diagnostisk og predictiv analyse inkl. forecast per produkt.

### Hent kontrakter

```bash
curl http://localhost:8001/contracts \
  -H "X-API-Key: dev-contract-key"
```

---

## Test

```bash
# Kør tests for begge services
cd contract_service && pytest -v
cd ../order_service && pytest -v
```

### Teststrategi (Testing Pyramid)

| Niveau | Hvad testes | Isolation |
|---|---|---|
| **Unit tests** | Domænelogik: aggregat-overgange, value object-validering, forretningsregler | Ingen netværks- eller databaseafhængigheder |
| **Integrationstests** | ACL-transformation: outbound til Contract API-format, inbound til `ProductCheckResult` | Mock-fixtures isolerer netværkslaget |
| **API-tests** | Samlede forretningsflow fra ordreindtag til SAP-videresendelse | Postman — importér OpenAPI fra `/docs` |

Domænelagets tests er fuldstændig afkoblet fra infrastruktur — en fejl i PostgreSQL eller Contract Service påvirker aldrig unit tests.

---

## CI/CD og DevSecOps

GitHub Actions kører automatisk ved push og pull requests til `main`:

```
Push/PR til main
       │
       ▼
┌─────────────────────────────────────┐
│  Test Job (matrix: parallel)        │
│  ├── contract_service: pytest -v    │
│  └── order_service: pytest -v       │
└─────────────────┬───────────────────┘
                  │ (kun hvis begge består)
                  ▼
┌─────────────────────────────────────┐
│  Build Job                          │
│  ├── Byg Docker image               │
│  └── Tag med git SHA                │
└─────────────────────────────────────┘
```

**Secrets** (`DB_PASSWORD`, `CONTRACT_API_KEY`, `ORDER_API_KEY`) håndteres via GitHub Secrets og injiceres som environment variables — aldrig hardcodet i koden eller commit-historikken.

**Rollback:** Images tagges med git SHA, så en specifik version altid kan genoprettes deterministisk.

---

## Observability: Prometheus + Grafana

Begge services eksponerer `/metrics` via `prometheus-fastapi-instrumentator`. Prometheus scraper metrics hvert 15. sekund. Grafana visualiserer dem i et live dashboard.

### Adgang

```
Grafana:    http://localhost:3000  (admin / admin)
Prometheus: http://localhost:9090/targets
```

### Dashboard: Arla RoW DS — Order Processing Observability

| Panel | Metric |
|---|---|
| HTTP requests per sekund | `rate(http_requests_total[1m])` |
| p95 latency | `histogram_quantile(0.95, ...)` |
| POST /orders total | `http_requests_total{handler="/orders", method="POST"}` |
| POST /orders 2xx (godkendt) | `...{status="2xx"}` |
| POST /orders 4xx (afvist) | `...{status="4xx"}` |
| Ordreflow over tid | 2xx vs 4xx per sekund |
| PostgreSQL forbindelser | `pg_stat_activity_count{state="active"}` |
| PostgreSQL inserts/sek | `rate(pg_stat_database_tup_inserted[1m])` |

---

## Power BI

Power BI Desktop forbindes direkte til PostgreSQL via den indbyggede connector:

- **Server:** `localhost:5432`
- **Database:** `arla_row`
- **Credentials:** username `arla`, password `arla` (lokal udvikling)

### Anbefalede dashboards

- Ordrevolumen per marked og distributør
- Status-fordeling (valideret vs. afvist) og fejlrate per kanal
- Forecast vs. faktisk volumen per produkt
- Rejection reasons — hvilke fejltyper er hyppigst?

---

## Projektstruktur

```
Eksamen_gruppe10/
├── arla-row-ds/
│   ├── contract_service/           # Contract Context (bounded context)
│   │   ├── app/
│   │   │   ├── domain/
│   │   │   │   ├── aggregates/     # DistributorContract (aggregate root)
│   │   │   │   ├── entities/       # Distributor, ContractLine
│   │   │   │   └── value_objects/  # ContractTerms, PricingTier, MarketRegion
│   │   │   ├── infrastructure/
│   │   │   │   ├── models.py       # SQLAlchemy ORM-modeller
│   │   │   │   └── repositories/   # ContractRepository
│   │   │   ├── api/
│   │   │   │   ├── routes/         # GET /contracts, check-endpoint
│   │   │   │   └── schemas.py      # Pydantic output-schemas
│   │   │   ├── auth.py             # API-nøgle autentificering
│   │   │   ├── config.py           # Environment variables
│   │   │   ├── database.py         # SQLAlchemy session
│   │   │   ├── main.py             # FastAPI entrypoint
│   │   │   └── seed.py             # Testdata til lokal udvikling
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── order_service/              # Order Context (bounded context)
│   │   ├── app/
│   │   │   ├── domain/
│   │   │   │   ├── aggregates/     # Order (aggregate root) + OrderLine
│   │   │   │   ├── events/         # OrderReceived, OrderValidated, OrderRejected
│   │   │   │   ├── services/       # OrderValidationService, DemandForecastService
│   │   │   │   └── value_objects/  # OrderStatus, Channel, Quantity
│   │   │   ├── infrastructure/
│   │   │   │   ├── acl/            # ContractClient (Anti-Corruption Layer)
│   │   │   │   ├── repositories/   # OrderRepository (PostgreSQL via SQLAlchemy)
│   │   │   │   ├── sap/            # SAP-adapter (mocket i MVP)
│   │   │   │   └── models.py       # SQLAlchemy ORM-modeller
│   │   │   ├── api/
│   │   │   │   ├── routes/         # POST /orders, GET /forecast
│   │   │   │   └── schemas.py      # Pydantic in/out-schemas
│   │   │   ├── auth.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── logging_config.py
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── grafana/
│   │   ├── dashboards/             # arla-row-ds-dashboard.json
│   │   └── provisioning/           # datasources + dashboards YAML
│   ├── prometheus/
│   │   └── prometheus.yml          # Scrape-konfiguration
│   ├── docker-compose.yml
│   └── .env.example
│
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions CI/CD pipeline
```

---

## Miljøer

| Miljø | Beskrivelse | Konfiguration |
|---|---|---|
| **Udvikling** | Lokalt via `docker-compose up` | `.env`-fil |
| **Produktion** | Azure Container Apps (fuld løsning) | GitHub Secrets + Azure Key Vault |

Samme Docker-image kører i alle miljøer — konfiguration injiceres via environment variables, aldrig hardcodet.

---

## Referencer

- Khononov, V. (2021). *Learning Domain-Driven Design*. O'Reilly Media.
- Indrasiri, K. & Suhothayan, S. (2021). *Design Patterns for Cloud Native Applications*. O'Reilly Media.
- Goniwada, S. (2022). *Cloud Native Architecture and Design*. Apress.
