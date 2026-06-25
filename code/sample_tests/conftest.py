"""PyTest configuration for sample tests."""

from apis.wp_api_client import authenticated_wp_client, wp_client

__all__ = ["wp_client", "authenticated_wp_client"]
