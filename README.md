# AttendanceTracker

A legacy Flask application for daily attendance entry, administrator-managed accounts and summary views. It demonstrates session-based authentication, role checks, parameterized SQLite queries and server-rendered forms.

This public repository is a **local engineering demonstration**. Use fictional records only. It is not a deployment package for an operational unit or an audited system for handling personnel or medical information.

## Run locally

Use Python 3.12 and a fresh checkout:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python init_db.py
python -m flask --app app run
```

Initialization asks for a new administrator password of at least 12 characters and refuses to overwrite an existing database. Sign in at `http://127.0.0.1:5000` as `superadmin`. No shared default password or populated database is distributed.

`ATTENDANCE_DATABASE` selects the local database file; `ATTENDANCE_SESSION_DIR` selects the session directory. Set `ATTENDANCE_SECRET_KEY` through your environment when a persistent signing key is needed. Without it, development uses a fresh random key at startup.

## Design

| Component | Responsibility |
|---|---|
| [`app.py`](app.py) | Login, account management, attendance entry and summaries |
| [`schema.sql`](schema.sql) | Empty account and attendance schema |
| [`init_db.py`](init_db.py) | Exclusive local database creation and administrator password hashing |
| [`templates/`](templates/) / [`static/`](static/) | Jinja views and browser interaction |

Users submit morning and afternoon attendance. Administrator routes manage accounts and review summaries. State is stored in local SQLite and filesystem sessions.

## Verify

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip_audit -r requirements.txt
```

Tests use temporary databases and sessions and cover initialization, authentication failures, role restrictions and login/logout. GitHub Actions runs these checks on pull requests and `main`.

## Boundaries and known limitations

- Database files, sessions, exports and environment files are ignored. Commit schema and fictional fixtures only. Removing a tracked file does not erase older Git history.
- This legacy application needs further CSRF, validation, rate-limit and deployment review before serving untrusted users. Run the development server on loopback.
- Daily rollover clears the previous attendance snapshot; this is not a historical attendance archive.
- The spreadsheet export reads a public example table; it does **not** export attendance. The report page is the implemented attendance summary.
- No software license is currently declared. Third-party dependencies and assets retain their own terms.
