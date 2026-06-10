# Outreach Key Server

[![CI](https://github.com/SucceedHQ/outreach-key-server/actions/workflows/ci.yml/badge.svg)](https://github.com/SucceedHQ/outreach-key-server/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)

**Access key management and lead tracking API for outreach automation campaigns.**

A Flask-based REST API that issues, validates, and monitors access keys for outreach automation scripts. Provides real-time analytics on leads processed, success rates, and per-key performance.

## Features

- Access key generation and management (CRUD)
- Per-key lead tracking with cumulative stats
- Real-time usage validation and authorization
- Admin web dashboard with analytics
- SQLite persistence (zero configuration)
- RESTful API design

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/keys` | List all keys with aggregate stats |
| `POST` | `/api/keys` | Create a new access key (`{"owner": "..."}`) |
| `DELETE` | `/api/keys/<key>` | Revoke an access key |
| `POST` | `/api/validate` | Validate an access key |
| `POST` | `/api/report` | Report leads/successes for a key |

### Example: Validate Key

```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"access_key": "JUDD-MASTER-KEY"}'
```

### Example: Report Leads

```bash
curl -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d '{"access_key": "JUDD-MASTER-KEY", "success": 5, "failed": 2, "skipped": 1}'
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python key_server.py

# Open the admin dashboard
open http://localhost:5000
```

The database is initialized automatically with a `JUDD-MASTER-KEY` for testing.

## Tech Stack

- **Framework:** Flask (Python)
- **Database:** SQLite via SQLAlchemy
- **Frontend:** HTML templates with admin dashboard
- **Auth:** Token-based key validation

## Deployment

The server can be deployed on Render, Heroku, or any Python-capable platform:

```bash
# Set the PORT environment variable for your platform
export PORT=5000
python key_server.py
```

## License

MIT
