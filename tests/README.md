# Test Structure Documentation

## Overview
The test structure has been reorganized to mirror the application structure, following Spring Boot testing conventions. This provides better organization and makes it easier to locate tests for specific components.

## Directory Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_integration_sqlite.py     # Integration tests (stays at root)
├── controllers/                   # Tests for app/controllers/
│   ├── __init__.py
│   ├── test_appController.py
│   ├── test_authServiceController.py
│   └── test_user_and_auth_controllers.py
├── lib/                          # Tests for app/lib/
│   ├── __init__.py
│   ├── test_cache.py
│   ├── test_resend.py            # Renamed from test__resend.py
│   ├── test_resend_wrapper.py
│   └── test_twilio_wrapper.py
├── models/                       # Tests for app/models/
│   ├── __init__.py
│   └── test_db_helpers.py
├── routes/                       # Tests for app/routes/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_routes_code.py
├── schemas/                      # Tests for app/schemas/
│   └── __init__.py
└── utils/                        # Tests for app/utils/
    ├── __init__.py
    ├── test_exception_handler.py
    └── test_logger_file.py
```

## Benefits of This Structure

1. **Mirror Application Structure**: Each test directory corresponds directly to an app directory
2. **Easy Navigation**: Find tests for specific components quickly
3. **Spring Boot Convention**: Follows Java/Spring Boot testing organization patterns
4. **Scalability**: Easy to add new tests in the appropriate location
5. **Modularity**: Each test package is self-contained with its own `__init__.py`

## Import Strategy

All tests use absolute imports from the `app` module:
```python
from app.controllers import appController
from app.lib.resend import send_email
from app.utils.errors import NotFound
```

This approach ensures that imports work correctly regardless of the test file's location in the directory structure.

## Running Tests

Tests can be run at any level:
```bash
# Run all tests
pytest tests/

# Run tests for a specific component
pytest tests/controllers/
pytest tests/lib/
pytest tests/routes/

# Run a specific test file
pytest tests/controllers/test_appController.py
```

## Adding New Tests

When adding new tests, place them in the directory that corresponds to the app component being tested:

- Controller tests → `tests/controllers/`
- Library/utility functions → `tests/lib/`
- Database models → `tests/models/`
- API routes → `tests/routes/`
- Schemas/validation → `tests/schemas/`
- Utilities → `tests/utils/`

## File Naming Convention

Follow the pattern `test_<module_name>.py` for consistency:
- `test_appController.py` for `app/controllers/appController.py`
- `test_resend.py` for `app/lib/resend.py`
- `test_health.py` for health-related route tests