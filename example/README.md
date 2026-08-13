# Petstore example

This folder is a complete **pytest-pyrest** example against the public
[Swagger Petstore](https://petstore.swagger.io) API. It is not part of the
plugin package (`code/pyrest/`). Use it as a template when adding your own API.

## Layout

| Path | Role |
|------|------|
| `test_petstore_api.py` | Pytest tests grouped by resource (pets, store, users) |
| `apis/petstore_api_client.py` | Domain client (`BaseAPIClient` subclass) and fixtures |
| `util_petstore.py` | Pydantic models, payloads, and assertion helpers |
| `conftest.py` | Re-exports fixtures so pytest can discover them |
| `env/test-environment.csv` | URLs and API key loaded into the environment |

## Prerequisites

From the **repository root**:

```bash
uv sync --extra dev
```

Tests hit `https://petstore.swagger.io/v2` over the network. Authenticated
pet operations use `PETSTORE_API_KEY` from `env/test-environment.csv`
(the public demo key is `special-key`).

## Run the example

All commands assume the repository root.

```bash
# Full example suite
uv run pytest example/

# Same suite (pytest testpaths already points here)
uv run pytest

# Only API-marked tests
uv run pytest -m api

# One test file
uv run pytest example/test_petstore_api.py

# One test class or method
uv run pytest example/test_petstore_api.py::TestPetstoreUsers
uv run pytest example/test_petstore_api.py::TestPetstoreUsers::test_logout_user

# Verbose plugin logging
uv run pytest example/ --log-level=DEBUG

# Write API logs to a file (creates parent dirs if needed)
uv run pytest example/ --log-file=logs/pytest-api.log
```

This repo’s `pyproject.toml` already passes
`--env-file=example/env/test-environment.csv`. To use a different CSV:

```bash
uv run pytest example/ --env-file=path/to/my-environment.csv
```

## What a passing run looks like

You should see collected tests under `example/test_petstore_api.py` and a
green pass for each. A few Petstore endpoints are shared globally (especially
store orders); those tests retry or use unique IDs so they stay stable.

If `PETSTORE_API_KEY` is missing, tests that use
`authenticated_petstore_client` skip instead of failing.

## Next step

To add another API the same way, follow [docs/ADDING_APIS.md](../docs/ADDING_APIS.md).
