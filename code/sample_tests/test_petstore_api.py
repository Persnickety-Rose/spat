"""Swagger Petstore API tests using the PyRest plugin framework."""

import uuid
from typing import Any, Dict

import pytest

pytestmark = pytest.mark.api


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def _pet_payload(name: str | None = None, status: str = "available") -> Dict[str, Any]:
    suffix = _unique_suffix()
    return {
        "id": int(suffix, 16) % 1_000_000_000,
        "name": name or f"doggie-{suffix}",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": status,
        "category": {"id": 1, "name": "Dogs"},
        "tags": [{"id": 1, "name": f"tag-{suffix}"}],
    }


def _user_payload(username: str | None = None) -> Dict[str, Any]:
    suffix = _unique_suffix()
    uname = username or f"user_{suffix}"
    return {
        "id": int(suffix, 16) % 1_000_000_000,
        "username": uname,
        "firstName": "Test",
        "lastName": "User",
        "email": f"{uname}@example.com",
        "password": "password123",
        "phone": "555-0100",
        "userStatus": 1,
    }


def _order_payload(pet_id: int = 1) -> Dict[str, Any]:
    suffix = _unique_suffix()
    return {
        "id": (int(suffix, 16) % 10) + 1,  # valid order IDs are 1-10 for GET
        "petId": pet_id,
        "quantity": 1,
        "status": "placed",
        "complete": False,
    }


class TestPetstorePets:
    """Pet resource tests — create then read/update/delete."""

    def test_add_pet(self, authenticated_petstore_client, assert_api):
        pet = _pet_payload()
        response = authenticated_petstore_client.add_pet(pet)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_api.json_contains(response, "id")
        assert_api.json_contains(response, "name", pet["name"])

    def test_get_pet_by_id(self, authenticated_petstore_client, assert_api):
        pet = _pet_payload()
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        response = authenticated_petstore_client.get_pet(pet_id)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert response.json["id"] == pet_id

    def test_update_pet(self, authenticated_petstore_client, assert_api):
        pet = _pet_payload(status="available")
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        updated = {**pet, "id": pet_id, "name": f"updated-{pet['name']}", "status": "sold"}
        response = authenticated_petstore_client.update_pet(updated)

        assert_api.status_code(response, 200)
        assert_api.json_contains(response, "name", updated["name"])
        assert_api.json_contains(response, "status", "sold")

    def test_find_pets_by_status(self, petstore_client, assert_api):
        response = petstore_client.find_pets_by_status(status="available")

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert isinstance(response.json, list)

    def test_update_pet_with_form(self, authenticated_petstore_client, assert_api):
        pet = _pet_payload()
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        new_name = f"form-{pet['name']}"
        response = authenticated_petstore_client.update_pet_with_form(
            pet_id, name=new_name, status="pending"
        )

        assert_api.status_code(response, 200)

    def test_delete_pet(self, authenticated_petstore_client, assert_api):
        pet = _pet_payload()
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        response = authenticated_petstore_client.delete_pet(pet_id)

        assert_api.status_code(response, 200)

    def test_get_pet_not_found(self, petstore_client, assert_api):
        response = petstore_client.get_pet(999999999)

        assert_api.status_code(response, 404)


class TestPetstoreStore:
    """Store inventory and order tests."""

    def test_get_inventory(self, authenticated_petstore_client, assert_api):
        response = authenticated_petstore_client.get_inventory()

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert isinstance(response.json, dict)

    def test_place_order(self, petstore_client, assert_api):
        order = _order_payload(pet_id=1)
        response = petstore_client.place_order(order)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_api.json_contains(response, "id")
        assert_api.json_contains(response, "petId")

    def test_get_order_by_id(self, petstore_client, assert_api):
        order = _order_payload(pet_id=1)
        create_response = petstore_client.place_order(order)
        assert_api.status_code(create_response, 200)
        order_id = create_response.json["id"]

        response = petstore_client.get_order(order_id)

        assert_api.status_code(response, 200)
        assert response.json["id"] == order_id

    def test_delete_order(self, petstore_client, assert_api):
        order = _order_payload(pet_id=1)
        create_response = petstore_client.place_order(order)
        assert_api.status_code(create_response, 200)
        order_id = create_response.json["id"]

        response = petstore_client.delete_order(order_id)

        assert_api.status_code(response, 200)


class TestPetstoreUsers:
    """User resource tests with unique usernames."""

    def test_create_user(self, petstore_client, assert_api):
        user = _user_payload()
        response = petstore_client.create_user(user)

        assert_api.status_code(response, 200)

    def test_get_user_by_name(self, petstore_client, assert_api):
        user = _user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.get_user(user["username"])

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_api.json_contains(response, "username", user["username"])

    def test_login_user(self, petstore_client, assert_api):
        user = _user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.login_user(user["username"], user["password"])

        assert_api.status_code(response, 200)

    def test_update_user(self, petstore_client, assert_api):
        user = _user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        updated = {**user, "firstName": "Updated", "lastName": "Name"}
        response = petstore_client.update_user(user["username"], updated)

        assert_api.status_code(response, 200)

    def test_delete_user(self, petstore_client, assert_api):
        user = _user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.delete_user(user["username"])

        assert_api.status_code(response, 200)
