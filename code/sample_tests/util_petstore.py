"""Shared Petstore models, payloads, and assertion helpers for sample tests."""

import uuid
from typing import Any, Dict, Literal

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
    suffix = unique_suffix()
    return {
        "id": (int(suffix, 16) % 10) + 1,  # valid order IDs are 1-10 for GET
        "petId": pet_id,
        "quantity": 1,
        "status": "placed",
        "complete": False,
    }
