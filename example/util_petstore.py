"""Shared Petstore models, payloads, and assertion helpers for sample tests."""

import uuid
from typing import Any, Dict, Literal, Tuple

import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError


class Category(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    name: str


class Tag(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    name: str


class Pet(BaseModel):
    """Pet schema from https://petstore.swagger.io/"""

    model_config = ConfigDict(strict=True)

    id: int
    name: str
    photoUrls: list[str]
    status: Literal["available", "pending", "sold"] | None = None
    category: Category | None = None
    tags: list[Tag] | None = None


class CategoryShape(BaseModel):
    """Category field names/types when present; all fields optional."""

    model_config = ConfigDict(strict=True)

    id: int | None = None
    name: str | None = None


class TagShape(BaseModel):
    """Tag field names/types when present; all fields optional."""

    model_config = ConfigDict(strict=True)

    id: int | None = None
    name: str | None = None


class PetShape(BaseModel):
    """Pet response shape for list endpoints.

    Checks known field names and types when present, without requiring
    every field (public Petstore data is often incomplete).
    """

    model_config = ConfigDict(strict=True)

    id: int | None = None
    name: str | None = None
    photoUrls: list[str | None] | None = None
    status: Literal["available", "pending", "sold"] | None = None
    category: CategoryShape | None = None
    tags: list[TagShape] | None = None


class Order(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    petId: int
    quantity: int
    status: Literal["placed", "approved", "delivered"]
    complete: bool
    shipDate: str | None = None


class User(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str
    firstName: str
    lastName: str
    email: str
    password: str
    phone: str
    userStatus: int


class ApiResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    code: int
    type: str
    message: str


def assert_json_types(
    response: Any,
    schema: type[BaseModel] | TypeAdapter[Any],
) -> Any:
    """Validate response.json field types against a Pydantic model or TypeAdapter."""
    assert hasattr(response, "json"), "Response is not JSON"
    try:
        if isinstance(schema, TypeAdapter):
            return schema.validate_python(response.json, strict=True)
        return schema.model_validate(response.json)
    except ValidationError as exc:
        raise AssertionError(f"Response JSON failed type validation:\n{exc}") from exc


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def pet_payload(name: str | None = None, status: str = "available") -> Dict[str, Any]:
    suffix = unique_suffix()
    return {
        "id": int(suffix, 16) % 1_000_000_000,
        "name": name or f"doggie-{suffix}",
        "photoUrls": ["https://example.com/photo.jpg"],
        "status": status,
        "category": {"id": 1, "name": "Dogs"},
        "tags": [{"id": 1, "name": f"tag-{suffix}"}],
    }


def user_payload(username: str | None = None) -> Dict[str, Any]:
    suffix = unique_suffix()
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


def order_payload(pet_id: int = 1) -> Dict[str, Any]:
    """Build an order body for POST /store/order.

    Order IDs are forced into 1–10 on purpose: Petstore's GET
    /store/order/{orderId} only returns 200 for that range (other IDs 400/404).
    Pets/users can use large random IDs; orders cannot. That tiny shared pool
    is why place-then-get/delete tests must use ``place_and_get_order`` rather
    than a single create + follow-up call.
    """
    suffix = unique_suffix()
    return {
        "id": (int(suffix, 16) % 10) + 1,
        "petId": pet_id,
        "quantity": 1,
        "status": "placed",
        "complete": False,
    }


def place_and_get_order(
    client: Any,
    assert_api: Any,
    *,
    pet_id: int = 1,
    attempts: int = 5,
) -> Tuple[Dict[str, Any], Any, Any]:
    """Place an order, then GET it; retry when the public store races us.

    Why retries are needed
    ----------------------
    ``order_payload`` must use IDs 1–10 (see that helper). Those IDs are a
    global namespace on https://petstore.swagger.io — any other client can
    overwrite or delete the same order between our POST and GET/DELETE.
    Pets and users are unaffected because they use large/unique keys.

    We only accept a GET that still matches the order we just placed (id,
    petId, quantity, status), so we do not treat someone else's order as ours.
    """
    for _ in range(attempts):
        order = order_payload(pet_id=pet_id)
        created = client.place_order(order)
        assert_api.status_code(created, 200)
        order_id = created.json["id"]

        fetched = client.get_order(order_id)
        if fetched.status != 200:
            continue
        body = fetched.json
        if (
            body.get("id") == order_id
            and body.get("petId") == order["petId"]
            and body.get("quantity") == order["quantity"]
            and body.get("status") == order["status"]
        ):
            return order, created, fetched

    pytest.fail(
        "Could not stably create+fetch order after "
        f"{attempts} attempts (shared Petstore order IDs 1–10)"
    )
