# Arla RoW DS — Order Intake & Validation Platform

En MVP der demonstrerer en intelligent front-end mellem distributører og Arlas
SAP-system. Løsningen modtager ordrer via et REST API, normaliserer og validerer
dem mod distributøraftaler, persisterer dem struktureret og videresender
validerede ordrer til SAP. Strukturerede ordredata eksponeres til Power BI.

> Udviklet som teknisk produkt (MVP) til 6.2 semestereksamen, *Design og
> implementering af digitale løsninger*, Erhvervsakademi København.

---

## Arkitektur

Løsningen består af to selvstændige services (to bounded contexts) og en database:

```
Distributør
    │  POST /orders
    ▼
┌─────────────────┐     ACL (HTTP)      ┌────────────────────┐
│  Order Service  │ ──────────────────▶ │  Contract Service  │
│  (Order Context)│   validér ordre     │ (Contract Context) │
└────────┬────────┘                     └─────────┬──────────┘
         │                                         │
         ▼                                         ▼
   ┌──────────────────────────────────────────────────┐
   │                  PostgreSQL                        │
   └──────────────────────────────────────────────────┘
         │                                         ▲
         │ (validerede ordrer)                     │ Power BI
         ▼                                          (direkte forbindelse)
   ┌──────────────┐
   │  SAP (mock)  │
   └──────────────┘
```

### Bounded contexts

| Context | Service | Ansvar |
|---|---|---|
| Order Context | `order_service` | Modtagelse, validering og persistering af ordrer + SAP-integration + forecast |
| Contract Context | `contract_service` | Distributøraftaler, priser og valideringsregler |

Order Service kalder Contract Service gennem et **Anti-Corruption Layer**
(`order_service/app/infrastructure/acl/`), så ændringer i kontraktmodellen ikke
forurener ordredomænet.

### DDD i koden

| DDD-koncept | Hvor i koden |
|---|---|
| Aggregate Root | `Order` (`order_service/.../aggregates/order.py`), `DistributorContract` |
| Entity | `OrderLine`, `Distributor`, `ContractLine` |
| Value Object | `OrderStatus`, `Channel`, `Quantity`, `PricingTier`, `ContractTerms`, `MarketRegion` |
| Domain Service | `OrderValidationService`, `DemandForecastService` |
| Domain Event | `OrderReceived`, `OrderValidated`, `OrderRejected` |
| Repository | `OrderRepository`, `ContractRepository` |

---

## Tech stack

- **Python 3.12** + **FastAPI** — REST API'er
- **PostgreSQL** + **SQLAlchemy** — persistering
- **scikit-learn** — demand forecast (analytics domain service)
- **Docker** + **docker-compose** — containerisering
- **GitHub Actions** — CI/CD
- **Power BI** — BI-dashboards (separat analytics-løsning)
- **Postman** — manuel API-test

---

## Kom i gang

### Forudsætninger
- Docker og docker-compose installeret

### 1. Klargør miljøvariabler
```bash
cp .env.example .env
```

### 2. Start hele stacken
```bash
docker-compose up --build
```
Dette starter PostgreSQL, Contract Service (port 8001) og Order Service (port 8000).

### 3. Seed kontraktdata
I et nyt terminalvindue:
```bash
docker-compose exec contract-service python -m app.seed
```
Dette opretter to distributøraftaler at validere ordrer imod.

### 4. Åbn API-dokumentationen
- Order Service: http://localhost:8000/docs
- Contract Service: http://localhost:8001/docs

---

## Eksempel: opret en ordre

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-order-key" \
  -d '{
    "distributor_id": "DIST-001",
    "channel": "EMAIL",
    "order_date": "2026-02-01",
    "lines": [
      {"product_code": "ARLA-MILK-1L", "quantity": 60}
    ]
  }'
```

En gyldig ordre valideres, persisteres, sendes til (mock) SAP og returnerer
status `FORWARDED_TO_SAP`. En ugyldig ordre (ukendt produkt eller for lav
mængde) returneres med status `REJECTED` og en årsag.

### Forecast (analytics)
```bash
curl http://localhost:8000/forecast/DIST-001 -H "X-API-Key: dev-order-key"
```

---

## Test

```bash
# Contract Service
cd contract_service && pytest -v

# Order Service
cd order_service && pytest -v
```

Teststrategi:
- **Unit tests** af domænelaget (forretningsregler, isoleret fra infrastruktur)
- **Validering** testes via `OrderValidationService`
- API-test foretages manuelt i Postman (importér OpenAPI fra `/docs`)

---

## CI/CD

`.github/workflows/ci.yml` kører automatisk ved push til `main`:
1. **Test** — kører pytest på begge services
2. **Build** — bygger Docker images (kun hvis tests består)
3. **Deploy** — skitseret; udfyldes med cloud-target

Secrets (databaseadgang, cloud-tokens) håndteres via **GitHub Secrets** og
injiceres som environment variables — aldrig i koden.

---

## Drift (operations)

| Hensyn | Implementering |
|---|---|
| **Logning** | Struktureret logning af alle vigtige hændelser (ordre modtaget/valideret/afvist/sendt til SAP) |
| **Overvågning** | `/health` endpoint på begge services |
| **Fejlhåndtering** | Eksplicitte HTTP-fejlkoder; ordrer afvises kontrolleret; 503 hvis Contract Service er nede |
| **Robusthed** | Services kan genstartes uafhængigt; ACL isolerer fejl mellem contexts |
| **Rollback** | CI/CD bygger versionerede images (tagget med git SHA), så forrige version kan redeployes |

---

## Miljøer

| Miljø | Beskrivelse |
|---|---|
| **Udvikling** | Lokalt via docker-compose |
| **Produktion** | Cloud-target (fx Azure App Service eller Railway), deployes via CI/CD |

Konfiguration adskiller miljøer via environment variables (`DATABASE_URL`,
`API_KEY` osv.) — samme image, forskellig konfiguration.

---

## Power BI

Power BI Desktop forbindes direkte til PostgreSQL (`localhost:5432`, database
`arla_row`) via den indbyggede PostgreSQL-connector. Anbefalede dashboards:
- Ordrevolumen per marked/distributør
- Status-fordeling (valideret vs. afvist) og fejlrate per kanal
- Forecast vs. faktisk volumen

---

## Projektstruktur

```
arla-row-ds/
├── contract_service/        # Contract Context
│   ├── app/
│   │   ├── domain/          # aggregates, entities, value_objects
│   │   ├── infrastructure/  # ORM-modeller, repository
│   │   ├── api/             # routes, schemas
│   │   ├── auth.py, config.py, database.py, main.py, seed.py
│   └── tests/
├── order_service/           # Order Context
│   ├── app/
│   │   ├── domain/          # aggregates, value_objects, events, services
│   │   ├── infrastructure/  # ORM, repository, acl/, sap/
│   │   ├── api/             # routes (orders, forecast), schemas
│   │   └── ...
│   └── tests/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
└── README.md
```
