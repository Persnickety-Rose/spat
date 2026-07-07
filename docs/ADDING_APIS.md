# Adding a New API

This guide explains how APIs are managed in **pytest-pyrest** and walks through adding a new API set step by step. The WordPress integration in `code/sample_tests/` is the reference implementation.

## How APIs Are Managed

The framework uses three layers:

```
Tests (test_*.py)
    ↓ fixtures: api_client, assert_api, or domain-specific client
Client layer (optional domain client, or built-in APIClient)
    ↓ wraps
Base HTTP layer (pyrest.API_Call.API)
    ↓ uses
requests library
```

| Layer | Location | Role |
|-------|----------|------|
| Base HTTP | `code/pyrest/API_Call.py` | Low-level `API` class. Every call returns an `API` object with `status`, `content`, `json`, etc. |
| Plugin | `code/pyrest/plugin.py` | Pytest plugin: loads env vars, provides `api_client` and `assert_api` fixtures |
| Domain client | `code/sample_tests/apis/` | Optional typed client with one method per endpoint (e.g. `wp_api_client.py`) |
| Tests | `code/sample_tests/test_*.py` | Pytest tests that use fixtures and assertion helpers |
| Config | `code/sample_tests/env/*.csv` | Environment variables loaded at test collection time |

### Two Ways to Call an API

**Option A — Generic client (quick start)**

Use the built-in `api_client` fixture for ad-hoc endpoint strings. No new files required.

```python
@pytest.mark.api
def test_list_items(api_client, assert_api):
    response = api_client.get("api/v1/items")
    assert_api.status_code(response, 200)
```

**Option B — Domain client (recommended for a full API surface)**

Create a dedicated client class with typed methods, fixtures, and tests grouped by resource. This is how WordPress is implemented and is the pattern to follow when adding a substantial API.

The rest of this guide covers **Option B**.

---

## Step-by-Step: Add a New API

The examples below use a fictional **Acme API** (`https://api.acme.example/v1`). Replace names, endpoints, and auth details with your own.

### Step 1: Plan Your API Surface

Before writing code, decide:

1. **Base URL** — Will you reuse `envURL` or add a dedicated variable (e.g. `ACME_API_URL`)?
2. **Authentication** — Basic auth, bearer token, API key header, or none?
3. **Endpoints** — List the resources and HTTP methods you need to test.
4. **Public vs authenticated** — Which operations require credentials?

Example plan:

| Method | Endpoint | Auth required |
|--------|----------|---------------|
| GET | `/v1/items` | No |
| GET | `/v1/items/{id}` | No |
| POST | `/v1/items` | Yes (API key) |
| DELETE | `/v1/items/{id}` | Yes (API key) |

---

### Step 2: Add Environment Variables

Add credentials and URLs to your environment CSV file.

**File:** `code/sample_tests/env/qa-environment.csv`

Format is two columns per row, no header:

```csv
envURL,http://localhost:8888
ACME_API_URL,https://api.acme.example
ACME_API_KEY,your_api_key_here
```

The plugin loads this file during test collection (`pytest_collection_modifyitems` in `plugin.py`). Values are written to `os.environ` and read by your client fixtures.

You can also pass a different file at runtime:

```bash
uv run pytest --env-file=path/to/my-environment.csv
```

---

### Step 3: Create the Domain Client

Create a new file under `code/sample_tests/apis/`.

**File:** `code/sample_tests/apis/acme_api_client.py`

Follow the WordPress client structure:

1. Import `API` from `pyrest.API_Call`
2. Define a client class with `__init__` for config (base URL, auth, headers)
3. Add a private `_create_api_instance()` helper
4. Add one public method per endpoint
5. Define pytest fixtures at the bottom of the same file

#### 3a. Client class and factory method

```python
import os
from typing import Any, Dict, Optional

import pytest
from pyrest.API_Call import API


class AcmeAPIClient:
    """Client for the Acme REST API."""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        verify_ssl: bool = True,
        cert_path: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.cert_path = cert_path
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _create_api_instance(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> API:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = self.default_headers.copy()
        if self.api_key:
            request_headers["Authorization"] = f"Bearer {self.api_key}"
        if headers:
            request_headers.update(headers)

        return API(
            address=url,
            method=method.upper(),
            data=data or "",
            header=request_headers,
            params=params or "",
            user="",
            password="",
            verify_ssl=self.verify_ssl,
            cert_path=self.cert_path,
        )
```

**Key pattern:** The client uses **composition**, not inheritance. It creates an `API` instance, calls `CallAPI()`, and returns the response object. See `WordPressAPIClient._create_api_instance` in `wp_api_client.py` for the canonical example.

#### 3b. Endpoint methods

Each method follows the same three steps: create instance → call API → return response.

```python
    def get_items(self, params: Optional[Dict[str, Any]] = None) -> API:
        api = self._create_api_instance(
            endpoint="/v1/items",
            method="GET",
            params=params,
        )
        api.CallAPI()
        return api

    def get_item(self, item_id: int) -> API:
        api = self._create_api_instance(
            endpoint=f"/v1/items/{item_id}",
            method="GET",
        )
        api.CallAPI()
        return api

    def create_item(self, name: str, description: str = "") -> API:
        if not self.api_key:
            raise ValueError("API key required for creating items")

        api = self._create_api_instance(
            endpoint="/v1/items",
            method="POST",
            data={"name": name, "description": description},
        )
        api.CallAPI()
        return api

    def delete_item(self, item_id: int) -> API:
        if not self.api_key:
            raise ValueError("API key required for deleting items")

        api = self._create_api_instance(
            endpoint=f"/v1/items/{item_id}",
            method="DELETE",
        )
        api.CallAPI()
        return api
```

For **basic auth** instead of a bearer token, pass `user=` and `password=` to `API()` (as WordPress does) rather than an `Authorization` header.

#### 3c. Pytest fixtures

Define fixtures in the same file, reading from environment variables:

```python
@pytest.fixture
def acme_client():
    """Unauthenticated or read-only Acme API client."""
    base_url = os.getenv("ACME_API_URL", os.getenv("envURL", "http://localhost:8888"))
    return AcmeAPIClient(base_url=base_url, verify_ssl=True)


@pytest.fixture
def authenticated_acme_client():
    """Acme API client with credentials. Skips test if key is missing."""
    base_url = os.getenv("ACME_API_URL", os.getenv("envURL", "http://localhost:8888"))
    api_key = os.getenv("ACME_API_KEY")

    if not api_key:
        pytest.skip("ACME_API_KEY environment variable required")

    return AcmeAPIClient(base_url=base_url, api_key=api_key, verify_ssl=True)
```

This mirrors the `wp_client` / `authenticated_wp_client` pattern in `wp_api_client.py`.

---

### Step 4: Register Fixtures in conftest.py

Export your new fixtures so pytest discovers them project-wide.

**File:** `code/sample_tests/conftest.py`

```python
"""PyTest configuration for sample tests."""

from apis.acme_api_client import acme_client, authenticated_acme_client
from apis.wp_api_client import authenticated_wp_client, wp_client

__all__ = [
    "acme_client",
    "authenticated_acme_client",
    "wp_client",
    "authenticated_wp_client",
]
```

Without this import, fixtures defined in `apis/` are not automatically available to test files unless those files import them directly.

---

### Step 5: Write Tests

Create a test file alongside the existing examples.

**File:** `code/sample_tests/test_acme_api.py`

```python
"""Tests for the Acme REST API."""

import pytest

pytestmark = pytest.mark.api


class TestAcmeItems:
    """Read-only item tests."""

    def test_get_items(self, acme_client, assert_api):
        response = acme_client.get_items()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert isinstance(response.json, list)

    def test_get_item_by_id(self, acme_client, assert_api):
        items_response = acme_client.get_items()
        assert_api.status_code(items_response, 200)

        if items_response.json:
            item_id = items_response.json[0]["id"]
            response = acme_client.get_item(item_id)

            assert_api.status_code(response, 200)
            assert response.json["id"] == item_id


class TestAcmeAuthenticatedOperations:
    """Tests that require an API key."""

    def test_create_item(self, authenticated_acme_client, assert_api):
        response = authenticated_acme_client.create_item(
            name="Test Item",
            description="Created by pytest",
        )

        assert_api.status_code(response, 201)
        assert_api.json_contains(response, "id")
        assert_api.json_contains(response, "name", "Test Item")
```

**Testing conventions used in this project:**

- Mark tests with `@pytest.mark.api` or set `pytestmark = pytest.mark.api` at module level
- Use `assert_api` helpers: `status_code`, `has_content`, `json_contains`, `success`, `failure`
- Group related tests into classes (`TestAcmeItems`, `TestAcmeAuthenticatedOperations`)
- Use `authenticated_*` fixtures for write operations; they auto-skip when credentials are missing
- Validate auth requirements in client methods with `raise ValueError(...)` for immediate feedback in unit-style usage

---

### Step 6: Run Your Tests

```bash
# Run all API-marked tests
uv run pytest -m api

# Run only your new test file
uv run pytest code/sample_tests/test_acme_api.py

# Run with a custom environment file
uv run pytest --env-file=code/sample_tests/env/qa-environment.csv code/sample_tests/test_acme_api.py

# Verbose API logging
uv run pytest --api-log-level=DEBUG code/sample_tests/test_acme_api.py -v
```

---

## Quick Reference Checklist

Use this when adding any new API:

- [ ] **Env vars** added to `code/sample_tests/env/qa-environment.csv` (or a custom CSV)
- [ ] **Client file** created at `code/sample_tests/apis/<name>_api_client.py`
  - [ ] `__init__` stores base URL, auth, SSL settings
  - [ ] `_create_api_instance()` builds and returns an `API` object
  - [ ] One public method per endpoint; each calls `api.CallAPI()` and returns `api`
  - [ ] Auth-guarded methods raise `ValueError` or fixtures use `pytest.skip`
  - [ ] `@pytest.fixture` definitions for unauthenticated and authenticated clients
- [ ] **conftest.py** updated to import and export new fixtures
- [ ] **Test file** created at `code/sample_tests/test_<name>_api.py`
  - [ ] Tests marked with `@pytest.mark.api`
  - [ ] Uses `assert_api` for assertions
  - [ ] Test classes grouped by resource or concern
- [ ] **Tests pass** against a reachable API instance

---

## Architecture Reference

```mermaid
flowchart TB
    subgraph tests [sample_tests/]
        T[test_acme_api.py]
        C[conftest.py]
        CL[apis/acme_api_client.py]
    end

    subgraph plugin [pyrest/]
        P[plugin.py]
        AC[APIClient fixture]
        AA[assert_api fixture]
    end

    subgraph core [pyrest/]
        API[API_Call.API]
    end

    T --> CL
    T --> AA
    C --> CL
    CL --> API
    AC --> API
    P --> AC
    P --> AA
    API --> REQ[requests]
```

---

## Existing Examples

| File | What it demonstrates |
|------|---------------------|
| `code/sample_tests/test_plugin_example.py` | Generic `api_client` + `assert_api` with endpoint strings |
| `code/sample_tests/apis/wp_api_client.py` | Full domain client with fixtures |
| `code/sample_tests/test_wordpress_api.py` | Test organization by resource, auth vs public, workflows |
| `code/pyrest/plugin.py` | Plugin fixtures, env loading, assertion helpers |
| `code/pyrest/API_Call.py` | Base `API` class all clients delegate to |

---

## Auth Patterns

Different APIs use different auth. Here is how to handle common cases in `_create_api_instance`:

| Auth type | How to configure |
|-----------|------------------|
| None | Omit `user`, `password`, and auth headers |
| Basic auth | Pass `user=` and `password=` to `API()` (WordPress pattern) |
| Bearer token | Set `Authorization: Bearer <token>` in headers |
| API key header | Set e.g. `X-API-Key: <key>` in headers |
| Per-request override | Accept optional `headers=` or `auth=` in public methods and merge into the request |

The generic `api_client` fixture supports per-request auth via `auth=(username, password)` and custom headers via the `headers=` kwarg. Domain clients can expose the same flexibility by adding optional parameters to `_create_api_instance` or individual endpoint methods.

---

## When to Use Which Approach

| Scenario | Approach |
|----------|----------|
| One or two smoke tests against an existing API | Generic `api_client` (Option A) |
| Many endpoints, reusable across test files | Domain client (Option B) |
| Shared auth logic and default headers | Domain client |
| CRUD workflows and resource-specific helpers | Domain client |
| Prototyping before committing to a client API | Start with `api_client`, refactor to domain client later |
