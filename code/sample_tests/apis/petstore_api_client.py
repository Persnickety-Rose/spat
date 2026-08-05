#!/usr/bin/env python
"""Petstore API client using the PyRest plugin framework."""

import os
from typing import Any
from urllib.parse import urlencode

import pytest
from pyrest import BaseAPIClient
from pyrest.API_Call import API


class PetstoreAPIClient(BaseAPIClient):
    """Client for the Swagger Petstore REST API."""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        verify_ssl: bool = True,
        cert_path: str | None = None,
    ):
        super().__init__(
            base_url,
            verify_ssl=verify_ssl,
            cert_path=cert_path,
        )
        self.api_key = api_key

    def _auth_headers(self) -> dict[str, str]:
        if self.api_key:
            return {"api_key": self.api_key}
        return {}

    def add_pet(self, pet: dict[str, Any]) -> API:
        """POST /pet — add a new pet to the store."""
        api = self._create_api_instance(endpoint="/pet", method="POST", data=pet)
        api.CallAPI()
        return api

    def get_pet(self, pet_id: int) -> API:
        """GET /pet/{petId} — find pet by ID."""
        api = self._create_api_instance(endpoint=f"/pet/{pet_id}", method="GET")
        api.CallAPI()
        return api

    def update_pet(self, pet: dict[str, Any]) -> API:
        """PUT /pet — update an existing pet."""
        api = self._create_api_instance(endpoint="/pet", method="PUT", data=pet)
        api.CallAPI()
        return api

    def find_pets_by_status(self, status: str = "available") -> API:
        """GET /pet/findByStatus — find pets by status."""
        api = self._create_api_instance(
            endpoint="/pet/findByStatus",
            method="GET",
            params={"status": status},
        )
        api.CallAPI()
        return api

    def update_pet_with_form(
        self, pet_id: int, name: str | None = None, status: str | None = None
    ) -> API:
        """POST /pet/{petId} — update a pet with form data."""
        form_fields: dict[str, str] = {}
        if name is not None:
            form_fields["name"] = name
        if status is not None:
            form_fields["status"] = status

        api = self._create_api_instance(
            endpoint=f"/pet/{pet_id}",
            method="POST",
            data=urlencode(form_fields),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        api.CallAPI()
        return api

    def delete_pet(self, pet_id: int) -> API:
        """DELETE /pet/{petId} — delete a pet."""
        api = self._create_api_instance(endpoint=f"/pet/{pet_id}", method="DELETE")
        api.CallAPI()
        return api

    def get_inventory(self) -> API:
        """GET /store/inventory — returns pet inventories by status."""
        api = self._create_api_instance(endpoint="/store/inventory", method="GET")
        api.CallAPI()
        return api

    def place_order(self, order: dict[str, Any]) -> API:
        """POST /store/order — place an order for a pet."""
        api = self._create_api_instance(
            endpoint="/store/order", method="POST", data=order
        )
        api.CallAPI()
        return api

    def get_order(self, order_id: int) -> API:
        """GET /store/order/{orderId} — find purchase order by ID."""
        api = self._create_api_instance(
            endpoint=f"/store/order/{order_id}", method="GET"
        )
        api.CallAPI()
        return api

    def delete_order(self, order_id: int) -> API:
        """DELETE /store/order/{orderId} — delete purchase order by ID."""
        api = self._create_api_instance(
            endpoint=f"/store/order/{order_id}", method="DELETE"
        )
        api.CallAPI()
        return api

    def create_user(self, user: dict[str, Any]) -> API:
        """POST /user — create a user."""
        api = self._create_api_instance(endpoint="/user", method="POST", data=user)
        api.CallAPI()
        return api

    def get_user(self, username: str) -> API:
        """GET /user/{username} — get user by username."""
        api = self._create_api_instance(endpoint=f"/user/{username}", method="GET")
        api.CallAPI()
        return api

    def update_user(self, username: str, user: dict[str, Any]) -> API:
        """PUT /user/{username} — update user."""
        api = self._create_api_instance(
            endpoint=f"/user/{username}", method="PUT", data=user
        )
        api.CallAPI()
        return api

    def delete_user(self, username: str) -> API:
        """DELETE /user/{username} — delete user."""
        api = self._create_api_instance(endpoint=f"/user/{username}", method="DELETE")
        api.CallAPI()
        return api

    def login_user(self, username: str, password: str) -> API:
        """GET /user/login — log user into the system."""
        api = self._create_api_instance(
            endpoint="/user/login",
            method="GET",
            params={"username": username, "password": password},
        )
        api.CallAPI()
        return api

    def logout_user(self) -> API:
        """GET /user/logout — log out current logged-in user session."""
        api = self._create_api_instance(endpoint="/user/logout", method="GET")
        api.CallAPI()
        return api

    def create_users_with_list(self, users: list[dict[str, Any]]) -> API:
        """POST /user/createWithList — create list of users."""
        api = self._create_api_instance(
            endpoint="/user/createWithList", method="POST", data=users
        )
        api.CallAPI()
        return api


@pytest.fixture
def petstore_client():
    """Unauthenticated Petstore API client."""
    base_url = os.getenv(
        "PETSTORE_API_URL", "https://petstore.swagger.io/v2"
    )
    return PetstoreAPIClient(base_url=base_url, verify_ssl=True)


@pytest.fixture
def authenticated_petstore_client():
    """Petstore API client with api_key header. Skips if key is missing."""
    base_url = os.getenv(
        "PETSTORE_API_URL", "https://petstore.swagger.io/v2"
    )
    api_key = os.getenv("PETSTORE_API_KEY")

    if not api_key:
        pytest.skip("PETSTORE_API_KEY environment variable required")

    return PetstoreAPIClient(
        base_url=base_url, api_key=api_key, verify_ssl=True
    )
