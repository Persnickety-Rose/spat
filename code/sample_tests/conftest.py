"""PyTest configuration for sample tests."""

from apis.petstore_api_client import (
    authenticated_petstore_client,
    petstore_client,
)
from apis.wp_api_client import authenticated_wp_client, wp_client

__all__ = [
    "authenticated_petstore_client",
    "authenticated_wp_client",
    "petstore_client",
    "wp_client",
]
