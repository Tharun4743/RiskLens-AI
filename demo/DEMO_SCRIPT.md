# RiskLens AI — 5-Minute Official Competition Presenter Script
**NexusTiq24 Problem Statement PS06: Transaction Risk Investigation Assistant**

---

### [00:00 – 00:30] 1. Problem Statement
**Presenter Action**: *Start on RiskLens AI Investigation Center Dashboard (`http://localhost:8000`). Point to the core engine indicators.*

**Spoken Script**:
> "Good day, judges. In modern banking operations and anti-money laundering units, risk analysts face tens of thousands of daily transactions. Traditional systems rely on noisy, rigid threshold alerts or black-box generative AI that hallucinates unsupported claims. 
> 
> Analysts waste hours manually calculating percentile deviations across account ledgers, tracing payment bursts, and reconstructing timelines. 
> 
> Today, we present **RiskLens AI** — an evidence-first transaction risk investigation assistant that analyzes multi-month customer histories, calculates mathematical behavioral baselines, deterministically flags anomalies across rules R001 to R004, and assists human investigators with grounded AI reasoning without ever declaring premature fraud."

---

### [00:30 – 01:00] 2. Product Architecture & Overview
**Presenter Action**: *Highlight the dashboard metrics (Active Cases, High Attention Required, Port 8000 Engine, Rules R001–R004 Active).*

**Spoken Script**:
> "RiskLens AI is built with a clear separation of concerns:
> 1. **Core Database Layer**: Scalable PostgreSQL with SQLAlchemy 2.0 connection pooling.
> 2. **Deterministic Risk Engine**: 100% Python-based mathematical baseline and rule evaluation.
> 3. **Traceable Evidence Store**: Every finding is hard-linked to underlying transaction ledger IDs.
> 4. **AI Reasoning Layer**: Google Gemini with strict hallucination validation and deterministic fallback.
> 
> Let's look at how an investigator conducts a case."

---

### [01:00 – 01:45] 3. Customer Behavioral Baseline
**Presenter Action**: *Navigate to 'Customers & Ingestion' (`#nav-btn-customers`). Select `CUST-005` (Rajesh Verma).*

**Spoken Script**:
> "Here in the Customer & Ingestion workspace, we see our customer profiles. What makes RiskLens AI unique is that **anomalies are customer-specific, not global**. A ₹50,000 transaction might be normal for a corporate entity, but highly unusual for a retail saver.
> 
> Let's examine customer `CUST-005` (Rajesh Verma). By clicking 'Analyze CUST-005', RiskLens AI instantly evaluates over 230 transactions covering the last 6 months.
> 
> Notice the **Customer Behavioral Baseline** card:
> - Historical median transaction: **₹1,715**
> - Typical active hours: **08:00 to 21:00**
> - Known merchant payees: **27 distinct counterparties**
> - Primary historical channels: **UPI and Debit Card**
> 
> The system has mathematically established what normal looks like for Rajesh."

---

### [01:45 – 02:45] 4. Deterministic Risk Detection (R001 – R004)
**Presenter Action**: *Scroll to 'Deterministic Risk Signals' on the Analysis Dashboard. Show all 4 triggered rules.*

**Spoken Script**:
> "When we compare recent account activity against this established baseline, the deterministic engine flags four distinct risk vectors:
> 
> 1. **Rule R001 (Unusually Large Transfer)**: Identifies a massive ₹4,80,000 NEFT transfer — a **279.8x surge** above the customer's median transaction.
> 2. **Rule R002 (New-Payee Rapid Burst)**: Detects 4 rapid transactions totaling ₹7,30,000 sent to newly seen entity 'XYZ Services' within a 47-minute window.
> 3. **Rule R003 (Odd-Hours Activity)**: Flags multiple late-night transactions executed between 02:14 and 03:01 AM — a zero-probability historical event for this daytime user.
> 4. **Rule R004 (Behavioral Shift)**: Surfaces a sudden 85% volumetric migration from retail UPI to high-value NEFT settlements.
> 
> Crucially, **Python code decided these rules triggered — not the LLM**. This guarantees 100% deterministic reproducibility."

---

### [02:45 – 03:30] 5. Traceable Evidence Investigation
**Presenter Action**: *Click 'View Evidence' (`#btn-view-evidence-F-001-01`) to open the Evidence Drawer.*

**Spoken Script**:
> "Every finding in RiskLens AI is fully traceable to immutable database records. 
> 
> When we open the Evidence Drawer for Rule R001:
> - **Source Transaction ID**: `TXN-2095`
> - **Observed Value**: `₹4,80,000.00`
> - **Customer Baseline**: `₹1,715.49`
> - **Mathematical Deviation**: `279.8x customer median`
> - **Timestamp & Payee**: `2026-06-18 02:14:00` via `NEFT`
> 
> An auditor can click any finding and inspect the exact ledger row that triggered the alert. There are no black-box scores or phantom transactions."

---

### [03:30 – 04:20] 6. Gemini AI Investigation Assistant & Grounded Q&A
**Presenter Action**: *Scroll to 'AI-Assisted Investigation Summary' and open the Analyst Chat Drawer (`#btn-open-chat`).*

**Spoken Script**:
> "Once the deterministic evidence packet is locked, Google Gemini generates an investigator-friendly briefing.
> 
> Notice what the AI provides:
> 1. **Objective Synthesis**: Summarizes the four converging risk vectors without declaring fraud.
> 2. **Explicit Unknowns**: Surfaces critical missing context, such as whether an underlying commercial invoice exists.
> 3. **Actionable Investigator Next Steps**: Recommends verifying counterparty 'XYZ Services' and requesting out-of-band customer confirmation.
> 
> In the **Analyst Q&A** panel, investigators can query the case directly. When we ask *'Why was this flagged?'*, the AI responds strictly grounded in the verified evidence packet.
> 
> If the API connection ever experiences downtime, RiskLens AI automatically falls back to verified deterministic templates, ensuring uninterrupted triaging."

---

### [04:20 – 04:45] 7. Formal Audit Case Report & PDF Export
**Presenter Action**: *Navigate to 'Audit & Reports' (`#nav-btn-reports`) and click 'Export PDF Report'.*

**Spoken Script**:
> "With a single click, RiskLens AI compiles a complete, publication-ready **Confidential Banking Audit Report**.
> 
> Clicking 'Export PDF' generates an immutable ReportLab PDF artifact containing:
> - Case ID and Customer Metadata
> - Overall Priority Score (`100/100 • HIGH`)
> - Triggered Rule Multipliers and Historical Baselines
> - Exact Transaction Evidence Citations
> - AI Executive Summary and Recommended Analyst Actions
> - Prominent Human-Investigator Disclaimer"

---

### [04:45 – 05:00] 8. Architecture & Human Judgement Disclaimer
**Presenter Action**: *Return to the main Investigation Center Dashboard (`#nav-btn-overview`). Point to the updated case audit trail.*

**Spoken Script**:
> "To conclude: RiskLens AI follows our cardinal architectural rule: **AI assists the investigator; AI does not decide fraud**. 
> 
> By combining deterministic behavioral statistics with grounded LLM reasoning, RiskLens AI cuts case triaging time by 80% while preserving total audit integrity.
> 
> Thank you."
