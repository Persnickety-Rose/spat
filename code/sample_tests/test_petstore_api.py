"""Swagger Petstore API tests using the PyRest plugin framework."""

import pytest
from pydantic import TypeAdapter

from util_petstore import (
    ApiResponse,
    Order,
    Pet,
    User,
    assert_json_types,
    order_payload,
    pet_payload,
    user_payload,
)

pytestmark = pytest.mark.api


class TestPetstorePets:
    """Pet resource tests — create then read/update/delete."""

    def test_add_pet(self, authenticated_petstore_client, assert_api):
        """POST /pet returns a Pet with all schema fields echoed back."""
        pet = pet_payload()
        response = authenticated_petstore_client.add_pet(pet)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_json_types(response, Pet)

        # Pet schema: id, category, name, photoUrls, tags, status
        # https://petstore.swagger.io/#/pet/addPet
        assert_api.json_contains(response, "id", pet["id"])
        assert_api.json_contains(response, "name", pet["name"])
        assert_api.json_contains(response, "photoUrls", pet["photoUrls"])
        assert_api.json_contains(response, "status", pet["status"])
        assert_api.json_contains(response, "category", pet["category"])
        assert_api.json_contains(response, "tags", pet["tags"])

    def test_get_pet_by_id(self, authenticated_petstore_client, assert_api):
        pet = pet_payload()
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        response = authenticated_petstore_client.get_pet(pet_id)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_json_types(response, Pet)
        assert response.json["id"] == pet_id

    def test_update_pet(self, authenticated_petstore_client, assert_api):
        pet = pet_payload(status="available")
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        updated = {**pet, "id": pet_id, "name": f"updated-{pet['name']}", "status": "sold"}
        response = authenticated_petstore_client.update_pet(updated)

        assert_api.status_code(response, 200)
        assert_json_types(response, Pet)
        assert_api.json_contains(response, "name", updated["name"])
        assert_api.json_contains(response, "status", "sold")

    def test_find_pets_by_status(self, petstore_client, assert_api):
        response = petstore_client.find_pets_by_status(status="available")

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_json_types(response, TypeAdapter(list[Pet]))

    def test_update_pet_with_form(self, authenticated_petstore_client, assert_api):
        pet = pet_payload()
        create_response = authenticated_petstore_client.add_pet(pet)
        assert_api.status_code(create_response, 200)
        pet_id = create_response.json["id"]

        new_name = f"form-{pet['name']}"
        response = authenticated_petstore_client.update_pet_with_form(
            pet_id, name=new_name, status="pending"
        )

        assert_api.status_code(response, 200)

    def test_delete_pet(self, authenticated_petstore_client, assert_api):
        pet = pet_payload()
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
        assert_json_types(response, TypeAdapter(dict[str, int]))

    def test_place_order(self, petstore_client, assert_api):
        order = order_payload(pet_id=1)
        response = petstore_client.place_order(order)

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_json_types(response, Order)
        assert_api.json_contains(response, "id")
        assert_api.json_contains(response, "petId")

    def test_get_order_by_id(self, petstore_client, assert_api):
        order = order_payload(pet_id=1)
        create_response = petstore_client.place_order(order)
        assert_api.status_code(create_response, 200)
        order_id = create_response.json["id"]

        response = petstore_client.get_order(order_id)

        assert_api.status_code(response, 200)
        assert_json_types(response, Order)
        assert response.json["id"] == order_id

    def test_delete_order(self, petstore_client, assert_api):
        order = order_payload(pet_id=1)
        create_response = petstore_client.place_order(order)
        assert_api.status_code(create_response, 200)
        order_id = create_response.json["id"]

        response = petstore_client.delete_order(order_id)

        assert_api.status_code(response, 200)


class TestPetstoreUsers:
    """User resource tests with unique usernames."""

    def test_create_user(self, petstore_client, assert_api):
        user = user_payload()
        response = petstore_client.create_user(user)

        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)

    def test_get_user_by_name(self, petstore_client, assert_api):
        user = user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.get_user(user["username"])

        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert_json_types(response, User)
        assert_api.json_contains(response, "username", user["username"])

    def test_login_user(self, petstore_client, assert_api):
        user = user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.login_user(user["username"], user["password"])

        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)

    def test_update_user(self, petstore_client, assert_api):
        user = user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        updated = {**user, "firstName": "Updated", "lastName": "Name"}
        response = petstore_client.update_user(user["username"], updated)

        assert_api.status_code(response, 200)

    def test_delete_user(self, petstore_client, assert_api):
        user = user_payload()
        create_response = petstore_client.create_user(user)
        assert_api.status_code(create_response, 200)

        response = petstore_client.delete_user(user["username"])

        assert_api.status_code(response, 200)
