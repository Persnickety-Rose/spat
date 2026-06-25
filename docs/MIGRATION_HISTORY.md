# Migration History

The traditional inheritance-based API test approach was migrated to the pytest-pyrest plugin framework.

## What changed

**Removed:** `WP_APIs.py`, `test_wpT01.py`, `test_wpT02.py`, and the `backup_traditional_approach/` directory.

**Replaced with:** pytest fixtures (`api_client`, `assert_api`, `wp_client`, `authenticated_wp_client`) and composition-based clients (`WordPressAPIClient` wrapping `API_Call.API`).

## Current approach

- Generic API examples: `code/sample_tests/test_plugin_example.py`
- WordPress examples: `test_wp_plugin_example.py`, `test_wpT01_migrated.py`, `test_wpT02_migrated.py`
- Plugin entry point: `pyrest.plugin` via pytest11 entry point

For the old traditional code, see git history before the migration commits.
