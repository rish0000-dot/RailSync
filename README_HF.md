---
title: RailSync 2.0
emoji: 🚂
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
tags:
  - railway
  - indian-railways
  - optimization
  - machine-learning
  - xgboost
  - or-tools
  - fastapi
  - react
  - digital-twin
  - maintenance-planning
pinned: true
license: mit
short_description: AI-powered automatic block planning & digital twin for Indian Railways
---

# 🚂 RailSync 2.0

**AI-Powered Automatic Block Planning & Digital Twin for Indian Railways**

> Built for Smart India Hackathon 2024 | NCR / PRYJ Division Prototype

## What is RailSync?

RailSync 2.0 is a real-time corridor maintenance planning and digital twin system that uses ML and constraint optimization to automatically generate zero-conflict maintenance possession schedules for Indian Railways.

### 🧠 4-Layer AI Pipeline

| Layer | Function | Tech |
|-------|----------|------|
| **Layer 0** | Master data ingestion (FOIS, SMMS, TDMS) | PostgreSQL / Supabase |
| **Layer 1** | 30-day failure risk forecasting per segment | XGBoost + lifelines survival analysis |
| **Layer 2** | Multi-department negotiation & evidence scoring | Weighted scoring engine |
| **Layer 3** | CP-SAT automatic block scheduling | Google OR-Tools |
| **Layer 4** | REST API orchestration & React dashboard | FastAPI + React 19 + Vite |

### 📊 Dashboard Pages

- **Overview** — Live risk heatmap, corridor KPIs, safety metrics
- **Corridor Digital Twin** — Visual segment map with real-time risk overlays
- **Train Timetable** — Day/Weekly possession schedule with zero-conflict guarantee
- **Segment Why? Risk** — XAI explanations for each segment's failure probability
- **What-If Sandbox** — Simulate rail fractures, OHE breakdowns, emergencies
- **Department Task Pool** — Multi-department block request management
- **Pareto Optimization** — Safety-first vs balanced vs throughput-first trade-offs
- **Feedback & Audit** — Closed-loop actual vs planned duration tracking

### 🤖 Model Accuracy

| Metric | Value |
|--------|-------|
| C-Index (ranking accuracy) | **95.45%** |
| Brier Score (30-day calibration) | **~0.000001** |
| Overrun Prediction Accuracy | **80.4%** |
| Segments covered | **46** |

## 🚀 Running Locally

```bash
# Backend
cd Backend && pip install -r requirements.txt
uvicorn app.main:app --port 8000

# Frontend
cd Frontend && npm install && npm run dev
```

## ⚙️ Environment Variables (HF Secrets)

Set these in your Hugging Face Space **Settings → Variables and Secrets**:

| Secret | Description |
|--------|-------------|
| `SUPABASE_DATABASE_URL` | PostgreSQL connection string |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role JWT |

> If no database is configured, the backend falls back to in-memory Layer 1 ML predictions.

## 🏗️ Architecture

```
HF Space (Docker, port 7860)
├── FastAPI Backend  →  /health, /risk/*, /tasks, /optimize/*, /plan/*, /feedback/*
└── React SPA        →  / (served as static files by FastAPI)
    ├── Overview Dashboard
    ├── Digital Twin
    ├── Train Timetable (Day + Weekly)
    ├── Segment Why? Risk
    ├── What-If Sandbox
    ├── Task Pool
    ├── Pareto Optimization
    └── Feedback & Audit
```
