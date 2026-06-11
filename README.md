# NEXAVARA Crisis Operating System

A production-ready multi-agent PQC (Post-Quantum Cryptographic) crisis response system.

This repository includes a live incident orchestration engine, agent-based analysis, coordinated crisis response, and an interactive dashboard for real-time monitoring.

## What this repo contains

- `main.py` — primary orchestrator that runs the PQC crisis workflow
- `web_dashboard.py` — Flask + SocketIO dashboard server
- `agents/` — AI and coordination agents
- `adapters/band_client.py` — in-memory messaging bus with contract validation
- `services/` — API clients and business impact services
- `messages/models.py` — Pydantic message schemas for message contract validation
- `static/` — dashboard frontend assets

## Prerequisites

- Python 3.10+ (Python 3.11 recommended)
- `pip` package manager

## Install dependencies

```bash
cd /workspaces/nexavara-crisisos-
pip install -r requirements.txt
```

## Environment configuration

The system loads API keys from `.env` using `python-dotenv`.

Create or update `.env` in the repository root with:

```bash
FEATHERLESS_API_KEY=your_featherless_api_key
FEATHERLESS_ENDPOINT=https://api.featherless.ai/v1/chat/completions
AI_ML_API_KEY=your_aiml_api_key
AI_ML_ENDPOINT=https://api.aimlapi.com/v1/chat/completions
FLASK_SECRET_KEY=your_flask_secret_key
```

If `AI_ML_API_KEY` or `FEATHERLESS_API_KEY` are missing, the system can still run in heuristic/demo mode, but AI-powered analysis and classification may be limited.

## Run the system

### 1. Run the core crisis workflow

```bash
cd /workspaces/nexavara-crisisos-
python main.py
```

### 2. Optional: Run the dashboard

```bash
cd /workspaces/nexavara-crisisos-
python web_dashboard.py
```

Then open:

```bash
http://localhost:5000
```

## Notes

- `main.py` is the real entry point for the PQC workflow.
- `web_dashboard.py` is the dashboard server for live front-end visualization.
- The `.env` file is required for API-backed AI/ML services.
- Use `python -m pip install -r requirements.txt` if your environment needs dependency updates.

## Troubleshooting

- If you see `ModuleNotFoundError`, ensure you are running from the repo root and `PYTHONPATH` includes `.`.
- If the dashboard port is in use, change it in `web_dashboard.py` or stop the conflicting service.
- If API calls fail, verify the keys and endpoints in `.env`.

## What to expect

The system will execute a PQC incident detection workflow, then print analysis, coordination, and decision outputs to the console. The dashboard can display live state updates and agent debate when it is running.

