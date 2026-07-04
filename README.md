# CivicAI

CivicAI is an image-first civic issue reporting application. This repository
currently contains the production-oriented application scaffold only; AI and
domain logic have intentionally not been implemented.

## Structure

```text
.
├── backend/
│   ├── agents/      # Future AI orchestration
│   ├── models/      # Data and domain models
│   ├── prompts/     # Version-controlled prompts
│   ├── routes/      # FastAPI endpoints
│   ├── services/    # Application services
│   ├── tools/       # External and agent tools
│   ├── utils/       # Shared helpers
│   └── main.py      # FastAPI entry point
├── frontend/
│   └── app.py       # Streamlit entry point
└── requirements.txt
```

## Local setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run the API:

```bash
uvicorn backend.main:app --reload
```

Run the frontend in a second terminal:

```bash
streamlit run frontend/app.py
```

The API health check is available at `http://127.0.0.1:8000/health`.
