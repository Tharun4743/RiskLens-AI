# 🔍 RiskLens AI — System Architecture & Forensic Pipeline

This document details the system topology, behavioral anomaly scoring algorithms, and automated Suspicious Activity Report (SAR) dossier generation pipeline for **RiskLens AI**.

---

## 1. Architectural Highlights
- **Evidence-First Anomaly Engine**: Scikit-Learn unsupervised ensemble learning (Isolation Forests and DBSCAN clustering) calculating multi-dimensional outlier scores from 16 behavioral features.
- **Automated Regulatory SAR Generation**: Google Gemini AI and structured Jinja2 templates converting complex mathematical anomaly indicators into standardized, regulatory-compliant Suspicious Activity Report narratives.
- **Forensic Hash Provenance**: Every drafted statement links back to cryptographically verified transaction IDs and timestamped ledger records.
- **Relational Core**: Supabase PostgreSQL database protected by Row-Level Security policies ensuring strict audit segregation.

---

## 2. Technical Documentation & Formal Report
The complete 12-page IEEE-standard technical architecture report is published in:
- **LaTeX Source**: [`docs/report/project-report.tex`](file:///c:/Users/tharu/Documents/GITHUB%20REPO/GITHUB%20MANAGER/RiskLens-AI/docs/report/project-report.tex)
- **Compiled PDF**: [`docs/report/project-report.pdf`](file:///c:/Users/tharu/Documents/GITHUB%20REPO/GITHUB%20MANAGER/RiskLens-AI/docs/report/project-report.pdf)
