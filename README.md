TRACK_ID=PS6
# RiskLens AI

Evidence-First Banking Transaction Risk Investigation Assistant for Banking Analysts.

## What the project does
RiskLens AI analyzes a customer's transaction history covering multiple months, establishes their statistical behavioral baseline, detects activity requiring attention using deterministic risk rules, explains the findings with Google Gemini using traceable evidence, and prepares structured cases for human investigation without making a fraud determination.

**Core Principle**: *AI assists the investigator. AI does not decide fraud.*

The application strictly enforces non-fraud terminology across all interfaces and AI outputs:
- **Never Displays**: "Fraud Detected", "Fraud Confirmed", "Customer is a Fraudster", "Definitely Fraud", or "Fraud Probability".
- **Displays Instead**: "Attention Required", "Investigation Recommended", "Requires Human Review", "Potentially Unusual Activity", "Insufficient Evidence", and "No Attention Required".

---

## Demo Video
- **Submission Demo Video Link**: [Watch RiskLens AI 3-Minute Demo Video](https://youtu.be/risklens-demo) *(Normal Routine Scenario vs. Multi-Vector Complex Investigation)*

---

## How to run it (One Command)

On a clean machine with Python 3.11:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the entire application (Backend + Pre-compiled Frontend + DB auto-initialization)
python app.py
```

The entire application starts immediately and is accessible at:
- **Web Application UI**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/health
- **API Documentation**: http://localhost:8000/docs

*No second terminal, no frontend build step, no manual database setup, and nothing that waits for a keypress.*

---

## Data and documents generated
All data and risk rules were engineered specifically for PS06 banking transaction risk investigation and are committed under `data/`:
1. **`data/customers.csv`**: 5 synthetic customer profiles with varying risk levels, transaction volumes, and behavioral patterns.
2. **`data/transactions.csv`**: 1,100+ transaction records over 6 months with date, description, payee, amount, and channel (UPI, NEFT, RTGS, CARD, ATM).
3. **`data/rules.json`**: Mathematical risk rules configuration (R001 Large Transfer, R002 New Payee Burst, R003 Odd-Hours Activity, R004 Behavioural Break).
4. **`data/demo_cases/`**: 5 individual scenario CSV files ready for drag-and-drop ingestion testing:
   - `normal_customer.csv` (CUST-001): 180 routine transactions, expected result: **NO ATTENTION REQUIRED**.
   - `large_transfer.csv` (CUST-002): High-value transfer anomaly triggering **R001**.
   - `new_payee_burst.csv` (CUST-003): Velocity burst to newly added payee triggering **R002**.
   - `odd_hours.csv` (CUST-004): 02:00–04:00 AM transactions triggering **R003**.
   - `complex_case.csv` (CUST-005): Multi-vector attack combining R001, R002, and R004 with correlation clustering.

---

## Problem addressed
Modern anti-money laundering (AML) and banking fraud investigation units face massive transaction volumes, noisy black-box alerts, and hallucinations from unconstrained generative AI. Analysts spend hours cross-referencing ledger tables, calculating percentile deviations manually, and tracing multi-vector payment bursts.

RiskLens AI solves this by introducing a deterministic-first architecture: mathematical statistical baselines and rules execute purely in Python, generating an unalterable evidence audit trail before Gemini is ever invoked to synthesize explanations.

---

## Production Architecture

```text
                                  VERCEL
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
           React + Vite UI                    Python FastAPI API
         (Humanized Palette)                 (Serverless Function)
                    │                                 │
                    │               ┌─────────────────┼─────────────────┐
                    │               ▼                 ▼                 ▼
                    │       Hosted PostgreSQL    Risk Engine       Gemini AI
                    │       (Supabase / Cloud)     (Python)     (Grounding & Q&A)
                    │               │                 │                 │
                    └───────────────┴──────────── Traceable ────────────┘
                                                   Evidence
```

- **Frontend**: React 18, TypeScript, TailwindCSS with Humanized Light & Dark modes, Recharts, and Lucide icons.
- **Backend API**: FastAPI on Python 3.11, SQLAlchemy 2.0 with PostgreSQL driver (`psycopg3`), serverless connection pooling (`pool_pre_ping=True`, `pool_recycle=300`).
- **Database**: Hosted PostgreSQL (via `DATABASE_URL` or Supabase) with automatic fallback to local SQLite for offline evaluation.
- **Risk Engine**: 100% deterministic Python rules (R001–R004), non-parametric baseline metrics, and correlation clustering.
- **AI Grounding**: Google Gemini (`gemini-2.5-flash`) with anti-hallucination validation against SQLite/PostgreSQL and zero-downtime deterministic fallback.

---

## Key capabilities
- **Customer Behavioral Baselines**: Customer-specific robust non-parametric baselines (median, IQR, 95th percentiles, active hourly windows, daily frequency, channel mix, known payees). Does not cross-compare customers.
- **Deterministic Rules Engine**:
  - **R001 (Unusually Large Transfer)**: Identifies transfers exceeding 95th percentile and materially exceeding typical amounts ($>4\times$ customer median).
  - **R002 (New Payee Burst)**: Identifies newly added/first-seen payees receiving $\ge 3$ rapid transactions within a short time window (e.g. 47–60 mins).
  - **R003 (Odd-Hours Activity)**: Evaluates late-night activity (00:00–05:00) against historical active hours.
  - **R004 (Behavioural Pattern Break)**: Detects macro channel shifts (e.g. UPI/Card shifting to 80% NEFT) and transaction volume surges.
- **Incident Correlation Engine**: Groups flagged transactions into correlated events by payee, time window, channel, and incident cluster.
- **Investigation Priority Scoring (0–100)**: Non-fraud triaging score (Normal 0–19, Low 20–49, Moderate 50–74, High 75–100) with rule-level contribution transparency.
- **Evidence-First Traceability**: Every finding maps to raw transaction IDs, observed values, baseline values, and mathematical deviations.
- **AI Hallucination Validation**: Strict guardrails verify all transaction IDs, amounts, and rule IDs returned by Gemini against the database. Any unsupported or invented claim is automatically rejected and reverted to deterministic findings.
- **Graceful Gemini Fallback**: Operates deterministically with 100% functionality if `GEMINI_API_KEY` is absent, times out, or errors.
- **Analyst Q&A Assistant**: In-dashboard interactive query tool answering analyst questions strictly grounded on case evidence.
- **Formal PDF Export**: Generates branded, publication-ready investigation reports via ReportLab.
- **CSV Ingestion & Validation**: Ingests external transaction logs with strict validation (dates, duplicate IDs, negative values, unsupported channels).

---

## Repository Structure
```
Nexus/
├── app.py                     # Local FastAPI entrypoint & Uvicorn runner
├── requirements.txt           # Clean pinned dependencies (SQLAlchemy 2.x, psycopg3, etc.)
├── README.md                  # PS06 Documentation with TRACK_ID=PS6
├── vercel.json                # Vercel serverless deployment configuration
├── .gitignore                 # Secrets, build artifacts, and DB exclusions
├── .env.example               # Template for DATABASE_URL, GEMINI_API_KEY, SUPABASE_*
│
├── api/                       # Vercel Serverless Function
│   └── index.py               # Serverless entrypoint exporting FastAPI app
│
├── scripts/
│   └── seed_demo_data.py      # Standalone CLI safe database seeder
│
├── src/
│   ├── api/                   # FastAPI Endpoints
│   │   ├── customers.py       # Customer retrieval & statistics
│   │   ├── transactions.py    # Transaction filtering & CSV upload
│   │   ├── investigations.py  # Investigation orchestration & chat
│   │   └── reports.py         # Report generation & PDF export
│   │
│   ├── engine/                # Deterministic Analysis Core
│   │   ├── baseline.py        # Non-parametric customer baseline engine
│   │   ├── rules.py           # R001, R002, R003, R004 implementation
│   │   ├── correlation.py     # Multi-transaction incident clustering
│   │   ├── scoring.py         # Investigation priority score (0-100)
│   │   └── risk_engine.py     # Master analysis orchestrator
│   │
│   ├── ai/                    # Gemini Integration Layer
│   │   ├── gemini_client.py   # google-genai client wrapper
│   │   ├── prompts.py         # Evidence-grounded system instructions
│   │   ├── schemas.py         # Pydantic schemas for AI output
│   │   └── report_generator.py# Hallucination validator & deterministic fallback
│   │
│   ├── evidence/              # Traceability
│   │   ├── evidence_store.py  # SQLAlchemy evidence persistence
│   │   └── citation.py        # Citation builder & evidence packet generator
│   │
│   ├── database/              # PostgreSQL / SQLite Database Layer
│   │   ├── database.py        # SQLAlchemy 2.0 engine, session pool, and health check
│   │   ├── models.py          # SQLAlchemy ORM models & Pydantic schemas
│   │   ├── seed_data.py       # Synthetic dataset generator & seeder
│   │   └── supabase_client.py # Supabase client integration
│   │
│   └── utils/                 # Utilities
│       ├── validation.py      # Strict CSV validator
│       ├── pdf_generator.py   # ReportLab PDF generator
│       ├── logging_config.py  # Secret-redacting structured logger
│       └── helpers.py         # Currency formatter (₹ INR) & math
│
├── data/
│   ├── customers.csv          # 5 demo customer profiles
│   ├── transactions.csv       # 1,100 synthetic transactions
│   ├── rules.json             # Configurable rule thresholds
│   └── demo_cases/            # Standalone test CSV files (CUST-001 to CUST-005)
│
├── frontend/
│   ├── package.json           # React / Tailwind / Recharts dependencies
│   ├── src/                   # React TypeScript source code (Light & Dark UI)
│   └── dist/                  # Pre-compiled static production bundle
│
└── tests/
    ├── test_database.py       # Database connection, ORM, and Supabase tests
    ├── test_baseline.py       # Baseline statistical calculations
    ├── test_rules.py          # R001 to R004 rule tests
    ├── test_correlation.py    # Multi-rule correlation & clusters
    ├── test_validation.py     # CSV validation tests (TC08-TC11)
    ├── test_api.py            # API endpoint lifecycle tests
    └── test_gemini_fallback.py# Fallback & hallucination validator tests
```

---

## Environment Variables

Create a `.env` file from `.env.example`:
```bash
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# PostgreSQL / Supabase Database Configuration
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/risklens
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key
SUPABASE_SECRET_KEY=your_secret_key
SUPABASE_JWKS_URL=https://your-project.supabase.co/auth/v1/.well-known/jwks.json
```

*(Note: If `DATABASE_URL` is omitted, the application automatically uses local SQLite for seamless offline testing. If `GEMINI_API_KEY` is omitted, the application runs with full functionality using the deterministic explanation fallback).*

---

## Local Development & Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize and seed database**:
   ```bash
   python scripts/seed_demo_data.py
   ```

3. **Start the application**:
   ```bash
   python app.py
   ```
   The application runs on `http://localhost:8000`:
   - Frontend UI: `http://localhost:8000/`
   - Health Check: `http://localhost:8000/api/health`
   - Interactive API Docs: `http://localhost:8000/docs`

---

## Vercel Production Deployment

RiskLens AI is configured for deployment on Vercel:

1. **Push to GitHub**:
   Ensure `vercel.json`, `api/index.py`, and `frontend/dist/` are committed.
2. **Import into Vercel**:
   - Framework Preset: `Other` (or auto-detected Vite)
   - Root Directory: `./`
3. **Configure Environment Variables in Vercel Dashboard**:
   - `DATABASE_URL`: Hosted PostgreSQL connection string (e.g. from Supabase / Neon / AWS RDS)
   - `GEMINI_API_KEY`: Google Gemini API key
   - `SUPABASE_URL`: Supabase project URL
   - `SUPABASE_SECRET_KEY`: Supabase secret key
4. **Deploy**:
   Vercel routes `/api/*` to the Python serverless function at `api/index.py` and serves the pre-compiled React single-page application.

---

## Testing

Run the comprehensive automated test suite with pytest:
```bash
python -m pytest -v
```
All 25 automated tests cover:
- Database connection, ORM models, and Supabase client
- Statistical baselines and outlier thresholds
- Deterministic risk rules R001 through R004
- Incident correlation and clustering
- CSV upload validation (missing columns, invalid amounts, negative amounts, duplicate IDs)
- Gemini grounding, hallucination rejection, and deterministic fallback
- Full API lifecycle

---

## Human-in-the-Loop Principle
RiskLens AI is purposefully architected as an **investigator assistant**, not an autonomous decision maker:
> **Human Investigator Review Required**: RiskLens AI identifies unusual activity and provides supporting evidence. It does not determine whether fraud occurred.
