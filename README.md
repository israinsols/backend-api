# Backend API

A small Flask API with CORS support, request rate limiting, file-based user storage, and an admin users view.

## Requirements

- Python 3.10+
- pip

## Setup

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run locally

```bash
python app.py
```

The API listens on `http://localhost:5000` by default. Set `PORT` to use another port.

## Endpoints

### `GET /`

Health check:

```json
{"status":"ok","message":"Backend is running"}
```

### `POST /api/save`

Accepts JSON with `username`, `password`, and a four-digit `pin`:

```json
{
  "username": "demo-user",
  "password": "example-only",
  "pin": "1234"
}
```

The route returns `400` for missing or invalid fields, `409` when the username already exists, and `200` after a successful write.

### `GET /admin/users?key=...`

Displays stored users when the query-string key matches `ADMIN_PASSWORD`.

## Data storage

On startup, the application creates `data/users.txt` if it does not exist. User records are stored as plain text blocks in that file. The `data/` directory is generated at runtime and should not be committed to source control.

## Deployment

The included `Procfile` runs the app with Gunicorn:

```text
web: gunicorn app:app
```

Before any deployment, configure a strong `ADMIN_PASSWORD` and review the security notes below.

## Security warning

This application currently stores passwords and PINs in plaintext and exposes them through the admin page. It is **not suitable for production or real user credentials**. Do not connect it to a real login flow or collect credentials from users.

For a legitimate production service, replace this storage model with:

- password hashing using a dedicated password-hashing library;
- encrypted or otherwise protected sensitive data storage;
- authentication and authorization for admin access;
- CSRF protection and stricter CORS configuration;
- secret management instead of default credentials;
- database-backed persistence with auditing and access controls.
