"""PyTest configuration for sample tests."""

from apis.petstore_api_client import (
    authenticated_petstore_client,
    petstore_client,
)

__all__ = [
    "authenticated_petstore_client",
    "petstore_client",
]
