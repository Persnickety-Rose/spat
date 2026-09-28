# Long Petstore API suite

`test_long_petstore_api.py` exercises the public Swagger Petstore at [https://petstore.swagger.io](https://petstore.swagger.io) (`/v2`). It sends live HTTP calls for pets, store orders, and users. Cases include successful creates, reads, updates, and deletes, plus rejected ids, bad bodies, missing records, and a blank login.

A full run is about **10 minutes**. There are 60 tests, and each one is given 10 seconds. The test logs when it starts, the request it is about to make, the HTTP status and a short body, and a pass or fail result. After the checks, it logs a heartbeat about every 3 seconds until that test's 10 seconds are up, so the console keeps moving for the whole run.

The public demo does not always match the published spec. An unknown pet status returns HTTP 200 and an empty list. A login with an empty username and password still returns a session. Those tests record that live behavior.

This is a shared server. Other people can change the same pets, orders, and users while the suite runs.

## Run it

Install dependencies once from the project root (`uv sync`). The machine needs a network path to `petstore.swagger.io`.

From the project root, in Command Prompt, PowerShell, or a Unix shell:

```text
uv run pytest code/sample_tests/test_long_petstore_api.py -v
```

If that reports a bad interpreter, call pytest through the virtualenv Python instead:

```text
.venv/bin/python -m pytest code/sample_tests/test_long_petstore_api.py -v
```

```text
.venv\Scripts\python -m pytest code/sample_tests/test_long_petstore_api.py -v
```

From any other folder, point `uv` at the project (use your real path):

```text
uv run --directory C:\path\to\spat pytest code/sample_tests/test_long_petstore_api.py -v
```

```text
uv run --directory /path/to/spat pytest code/sample_tests/test_long_petstore_api.py -v
```

Logs are printed as the tests run (`log_cli` is already on in `pyproject.toml`). Each line is timestamped and comes from the `petstore.longrun` logger.

## Run part of it

A subset is shorter than 10 minutes, because only the selected tests use their 10-second slices.

```text
uv run pytest code/sample_tests/test_long_petstore_api.py -v -k "order or user"
```

The file is marked `slow` and `api`. To run the other sample tests and skip this file:

```text
uv run pytest -m "not slow"
```
