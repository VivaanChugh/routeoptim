# Contributing

Thanks for helping improve Route Optimizer!

## Setup

**Backend** (Python 3.9+):

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000
```

**Frontend** (Node 20):

```bash
cd frontend
npm ci
npm run dev                     # http://localhost:5173
```

## Before opening a PR

CI runs these checks, so please run them locally first:

```bash
# backend
cd backend && pytest

# frontend
cd frontend && npm run lint && npm run build
```

Lint runs with `--max-warnings 0`, so warnings fail the build.

## Guidelines

- Branch from `main` and keep each PR focused on one change.
- Add or update tests for behavior changes (`backend/tests`).
- Use clear commit messages, e.g. `fix: ...`, `test: ...`, `docs: ...`.
- Don't commit generated summary/status markdown files.
