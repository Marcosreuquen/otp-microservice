# One time password with FastAPI

This project is a microservice authentication using FastAPI, designed to provide an additional security layer to your applications.

# Features

- MFA (multiple factor authentication) supports as Whatsapp, SMS and email
- Application registration, modification and deletion
- User registration, login and logout
- Code generation and verification
- Status of OTP

# One time password microservice (FastAPI)

Lightweight TOTP/OTP microservice built with FastAPI. This project provides application-level OTP registration, generation and verification using email, SMS and WhatsApp delivery backends.

Features
--------
- MFA support: WhatsApp, SMS and email
- Application registration, modification and deletion
- User registration, login and logout
- Code generation and verification

Quick endpoints summary
- `/api/code` — generation and verification of TOTP codes
- `/api/otp` — registration and verification of OTP flows
- `/api/auth` — user authentication (login/logout)
- `/api/app` — manage registered applications

Tech stack
----------
- FastAPI
- SQLModel (Postgres)
- pyotp (OTP generation)
- Resend (email), Twilio (SMS/WhatsApp)

Project layout
--------------
Standard layout used in this repo:

```
. 
├── app
│   ├── lib        # third-party library wrappers and clients
│   ├── routes     # FastAPI routers
│   ├── schemas    # Pydantic/SQLModel schemas
│   ├── controllers# business logic called by routes
│   ├── models     # database models (SQLModel)
│   ├── utils      # helpers, logging, errors, middlewares
│   └── main.py    # FastAPI app entrypoint
├── requirements.txt
├── docker-compose.yml
└── pytest.ini
```

Error handling
--------------
This project uses domain exceptions and a helper `require(condition, exc)` in `app/utils/errors.py`. A global FastAPI handler converts exceptions into structured JSON responses.

Installation
------------
Clone and install:

```bash
git clone https://github.com/marcosreuquen/otp-microservice.git
cd otp-microservice
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Environment
-----------
Copy the example `.env` and update credentials:

```bash
cp .env.example .env
```

Database
--------
The app uses Postgres in production. For local development you can run Postgres with Docker:

```bash
docker run -p 5432:5432 -e POSTGRES_PASSWORD=your_password postgres
```

Run the app
----------

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs are available at http://localhost:8000/docs (Swagger UI).

Tests and coverage
------------------
Tests are written with `pytest`. The repository includes a `pytest.ini` that generates test artifacts into `reports/` (this folder is gitignored). To run tests locally:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

After running tests `reports/` will contain:

- `reports/junit.xml` — JUnit-style test results
- `reports/coverage.xml` — coverage XML
- `reports/coverage_html/` — human-friendly HTML coverage report (open `index.html`)

Redis (cache)
-------------
Redis is used for rate limiting and short-lived OTP storage. The redis client is wired in `app/lib/cache.py` and injected into routes with `Depends(get_redis)`.

Run Redis locally with Docker (or via the project's docker-compose):

```bash
docker run -p 6379:6379 redis:7
```

The code is resilient to Redis failures: where Redis is unavailable the application falls back to permissive defaults so functionality continues.

Contribution
------------
PRs welcome — fork the repo, create a feature branch and open a PR. Tests and a short description are appreciated.

Contact
-------
Find me at: https://marcosdiaz.dev
