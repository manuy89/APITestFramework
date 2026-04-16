# API Test Framework

A robust, production-ready API test automation framework built with Python and pytest, using [ReqRes](https://reqres.in) as the target API.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core language |
| pytest | Test runner |
| requests | HTTP client |
| SQLite | Test data storage |
| python-dotenv | Secrets management |
| pytest-xdist | Parallel test execution |
| pytest-html | HTML test reports |

---

## Project Structure

```
APITestFramework/
├── config/
│   ├── config.json              # shared endpoints + timeout
│   ├── paths.py                 # central path definitions using pathlib
│   └── environments/
│       ├── dev.json             # dev base URL
│       ├── staging.json         # staging base URL
│       └── prod.json            # prod base URL
├── utils/
│   ├── api_client.py            # HTTP client with logging + error handling
│   ├── assertions.py            # centralized assertions with nested field support
│   ├── db_client.py             # SQLite client
│   ├── logger.py                # thread-safe QueueHandler logger
│   └── repositories/
│       ├── auth_repository.py   # auth table queries
│       └── user_repository.py   # users table queries
├── test_data/
│   ├── setup_db.py              # SQLite DB initializer
│   ├── test_db.sqlite           # auto-generated test database
│   └── payloads/
│       ├── auth.json            # auth request payloads
│       └── users.json           # user request payloads
├── tests/
│   ├── test_auth.py             # login + register tests
│   └── test_users.py            # CRUD tests for users
├── logs/
│   ├── test_run.log             # merged log (parallel runs)
│   ├── test_run_gw0.log         # worker 0 log (parallel runs)
│   └── report.html              # HTML test report
├── conftest.py                  # fixtures + pytest hooks
├── pytest.ini                   # pytest configuration
├── requirements.txt             # dependencies
├── .env                         # secrets (not committed)
├── .env.example                 # secrets template
└── .gitignore
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd APITestFramework
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```
API_KEY=your_api_key_here
API_EMAIL=your_email_here
API_PASSWORD=your_password_here
```

> Get a free API key from [app.reqres.in/api-keys](https://app.reqres.in/api-keys)

### 5. Run the tests

```bash
pytest                          # single run, dev environment (default)
pytest --env=staging            # run against staging
pytest --env=prod               # run against prod
pytest -n auto                  # parallel run using all CPU cores
pytest -n 4                     # parallel run using 4 workers
pytest --reset-db               # force reset the test database
pytest -n auto --reset-db       # parallel run + reset DB
```

---

## Key Features

### Environment Support
Switch between environments using the `--env` flag. Each environment has its own config file under `config/environments/`.

### Secrets Management
Sensitive values (`API_KEY`, `API_EMAIL`, `API_PASSWORD`) are stored in `.env` and never committed to version control.

### Test Data Layer
- **SQLite** stores test scenarios and expected values
- **JSON payloads** store request bodies per endpoint
- **Repository pattern** abstracts all SQL queries away from tests

### Centralized Assertions
`AssertionHelper` provides reusable assertion methods with clear error messages:
```python
assert_helper.assert_status_code(response, 200)
assert_helper.assert_key_in_response(response, "token")
assert_helper.assert_field_value(response, "data.email", "user@example.com")  # nested fields supported
assert_helper.assert_schema(response, ["id", "name", "email"])
```

### Thread-Safe Logging
Uses Python's `QueueHandler` to serialize log writes across parallel workers. Logs are written per worker and merged into a single `test_run.log` after the session.

```
logs/
├── test_run.log        ← full merged log
├── test_run_gw0.log    ← worker 0 only
└── test_run_gw1.log    ← worker 1 only
```

### HTML Report
Auto-generated after every run at `logs/report.html`.

---

## Adding New Tests

### 1. Add endpoint to `config/config.json`
```json
{
  "endpoints": {
    "products": {
      "base": "/products",
      "single": "/products/{id}"
    }
  }
}
```

### 2. Add payload to `test_data/payloads/products.json`
```json
{
  "create_product": { "name": "Widget", "price": 9.99 }
}
```

### 3. Add test data to `test_data/setup_db.py`

### 4. Add repository under `utils/repositories/product_repository.py`

### 5. Add fixture in `conftest.py`

### 6. Write tests in `tests/test_products.py`

---

## Environment Variables

| Variable | Description |
|---|---|
| `API_KEY` | ReqRes API key |
| `API_EMAIL` | Login email |
| `API_PASSWORD` | Login password |

---

## Logs

| File | Description |
|---|---|
| `logs/test_run.log` | Merged log from all workers |
| `logs/test_run_gw{n}.log` | Individual worker log |
| `logs/report.html` | HTML test report |

Each test in the log is clearly separated:
```
============================================================
TEST START: tests/test_auth.py::TestAuth::test_login_success
============================================================
... request / response / assertion logs ...
------------------------------------------------------------
TEST END: tests/test_auth.py::TestAuth::test_login_success | STATUS: PASSED
============================================================
```
