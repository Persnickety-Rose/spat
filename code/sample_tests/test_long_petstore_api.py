"""Long Swagger Petstore run against https://petstore.swagger.io/v2.

The full file is sized to take about 10 minutes. Each test calls the live
API, logs the call and the result, then keeps a heartbeat on the console
every few seconds until its time slice ends.

Negative cases follow the public demo, which is looser than the published
Swagger spec: an unknown status filter returns an empty list, and a blank
login still opens a session.

Attributes:
    FULL_SUITE_CASES (int): Number of collected tests the 10 minutes is
        divided across.
    SUITE_TARGET_SECONDS (int): Target length of a full run, in seconds.
    PER_TEST_SECONDS (float): Time slice each test is paced to, in seconds.
    HEARTBEAT_SECONDS (float): Seconds between heartbeat log lines.
    BANNER_WIDTH (int): Width of the per-test banner box, in characters.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from typing import Any, Callable

import pytest

from util_petstore import (
    ApiResponse,
    Pet,
    User,
    assert_json_types,
    order_payload,
    pet_payload,
    user_payload,
)

pytestmark = [pytest.mark.api, pytest.mark.slow]

logger = logging.getLogger("petstore.longrun")
logger.setLevel(logging.INFO)

# 60 collected cases * 10 seconds = about 10 minutes for the whole file.
FULL_SUITE_CASES = 60
SUITE_TARGET_SECONDS = 10 * 60
PER_TEST_SECONDS = SUITE_TARGET_SECONDS / FULL_SUITE_CASES
HEARTBEAT_SECONDS = 3.0
BANNER_WIDTH = 60

_suite_started = time.monotonic()
_tests_started = 0


def _body_text(response: Any, limit: int = 180) -> str:
    """Return the response body as one line of text, cut to a maximum length.

    Args:
        response: API call result from the PyRest client.
        limit: Maximum number of characters to keep before adding "...".

    Returns:
        The decoded body with whitespace collapsed, or an empty string when
        the response has no content.
    """
    content = getattr(response, "content", b"") or b""
    if isinstance(content, bytes):
        text = content.decode("utf-8", errors="replace")
    else:
        text = str(content)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _summarize(response: Any) -> str:
    """Build a short log line describing a response.

    Args:
        response: API call result from the PyRest client.

    Returns:
        The HTTP status followed by a short body. List bodies also include
        their length.
    """
    status = getattr(response, "status", "?")
    payload = getattr(response, "json", None)
    if isinstance(payload, list):
        return f"HTTP {status} list length {len(payload)} {_body_text(response, 120)}"
    if isinstance(payload, dict):
        return f"HTTP {status} {_body_text(response)}"
    text = _body_text(response)
    return f"HTTP {status} {text or '<empty body>'}"


def _log_banner(number: int, total: int, name: str) -> None:
    """Log a boxed banner with the test number, start time, and test name.

    Args:
        number: Position of this test in the run, starting at 1.
        total: Number of collected tests, used to zero-pad the number.
        name: Test name. Names too long for the box end with "...".
    """
    digits = max(2, len(str(total)))
    prefix = f"#  {number:0{digits}d} - {datetime.now():%H:%M:%S} - "
    room = BANNER_WIDTH - len(prefix) - 2
    if len(name) > room:
        name = name[: room - 3] + "..."
    border = "#" * BANNER_WIDTH
    logger.info(border)
    logger.info("%s%s #", prefix, name.ljust(room))
    logger.info(border)


def _message(response: Any) -> str:
    """Return the ``message`` field of a JSON response.

    Args:
        response: API call result from the PyRest client.

    Returns:
        The ``message`` value when the body is a JSON object, otherwise the
        body text.
    """
    payload = getattr(response, "json", None)
    if isinstance(payload, dict):
        return str(payload.get("message", ""))
    return _body_text(response)


def _raw_call(
    client: Any,
    endpoint: str,
    method: str = "GET",
    data: Any = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """Send a request that the Petstore client has no method for.

    Args:
        client: Petstore client that supplies the base URL and default
            headers.
        endpoint: Path under the base URL, for example ``/pet/abc``.
        method: HTTP method to send.
        data: Request body. Dicts are sent as JSON; strings are sent as is.
        params: Query string parameters.
        headers: Headers added to, or replacing, the client defaults.

    Returns:
        The completed API call, with ``status``, ``content``, and ``json``
        set.
    """
    api = client._create_api_instance(
        endpoint=endpoint,
        method=method,
        data=data,
        params=params,
        headers=headers,
    )
    api.CallAPI()
    return api


def _order(
    status: str = "placed",
    order_id: int | None = None,
    quantity: int = 1,
) -> dict[str, Any]:
    """Build an order payload with a chosen status, id, and quantity.

    Args:
        status: Order status to send.
        order_id: Order id to use. When omitted, a random id from 1 to 10 is
            used.
        quantity: Number of pets in the order.

    Returns:
        An order body ready for ``POST /store/order``.
    """
    payload = order_payload()
    payload["status"] = status
    payload["quantity"] = quantity
    if order_id is not None:
        payload["id"] = order_id
    return payload


class PacedCase:
    """Logs one test, then heartbeats until its slice of the 10 minutes ends.

    Attributes:
        name: Test name as pytest reports it, including parameters.
        purpose: First line of the test's docstring.
        started: Monotonic time when the test started.
        deadline: Monotonic time when the test's slice ends.
        closed: True once ``finish`` has been called.
        last_summary: Most recent response summary or result message.
    """

    def __init__(self, request: pytest.FixtureRequest, number: int):
        """Log the banner, start line, and purpose for a test.

        Args:
            request: Pytest request for the running test.
            number: Position of this test in the run, starting at 1.
        """
        self.name = request.node.name
        doc = (getattr(request.function, "__doc__", None) or "").strip()
        self.purpose = doc.splitlines()[0] if doc else self.name
        self.started = time.monotonic()
        self.deadline = self.started + PER_TEST_SECONDS
        self.closed = False
        self.last_summary = ""
        _log_banner(number, len(request.session.items), self.name)
        logger.info("START %s", self.name)
        logger.info("  purpose: %s", self.purpose)

    def call(self, description: str, func: Callable[[], Any]) -> Any:
        """Run one API call and log it.

        A heartbeat is logged every few seconds while the call is still
        waiting on the server.

        Args:
            description: Short label for the request, such as
                ``GET /pet/123``.
            func: Callable that sends the request and returns the response.

        Returns:
            The response returned by ``func``.
        """
        logger.info("  CALL %s", description)
        stop = threading.Event()

        def pulse() -> None:
            """Log a heartbeat every few seconds until ``stop`` is set."""
            beat = 0
            while not stop.wait(HEARTBEAT_SECONDS):
                beat += 1
                logger.info(
                    "  heartbeat wait %d | %s | still calling %s | suite %.0fs",
                    beat,
                    self.name,
                    description,
                    time.monotonic() - _suite_started,
                )

        worker = threading.Thread(target=pulse, name="petstore-heartbeat", daemon=True)
        worker.start()
        t0 = time.monotonic()
        try:
            response = func()
        finally:
            stop.set()
            worker.join(timeout=2)
        elapsed = time.monotonic() - t0
        summary = _summarize(response)
        self.last_summary = summary
        logger.info("  RESPONSE %.2fs %s", elapsed, summary)
        return response

    def finish(self, summary: str) -> None:
        """Log a pass, then heartbeat until the test's time slice ends.

        Args:
            summary: One-line description of what the test confirmed.
        """
        self.closed = True
        self.last_summary = summary
        logger.info("  RESULT PASS %s — %s", self.name, summary)
        beat = 0
        while True:
            remaining = self.deadline - time.monotonic()
            if remaining < 0.25:
                break
            beat += 1
            logger.info(
                "  heartbeat %d | %s | %s | %.0fs left in this test | suite %.0fs / %.0fs",
                beat,
                self.name,
                summary,
                remaining,
                time.monotonic() - _suite_started,
                SUITE_TARGET_SECONDS,
            )
            time.sleep(min(HEARTBEAT_SECONDS, remaining))
        logger.info(
            "  END %s in %.1fs",
            self.name,
            time.monotonic() - self.started,
        )


@pytest.fixture(scope="module", autouse=True)
def _long_suite_banner():
    """Log the suite start and finish, and reset the test counter.

    Yields:
        None. The suite's tests run while this fixture is suspended.
    """
    global _suite_started, _tests_started
    _suite_started = time.monotonic()
    _tests_started = 0
    logger.info(
        "Long Petstore suite starting: %d cases, %.1fs each, "
        "target %.0f minutes, heartbeat every %.0fs.",
        FULL_SUITE_CASES,
        PER_TEST_SECONDS,
        SUITE_TARGET_SECONDS / 60,
        HEARTBEAT_SECONDS,
    )
    yield
    elapsed = time.monotonic() - _suite_started
    logger.info(
        "Long Petstore suite finished in %.1f minutes (%.0fs).",
        elapsed / 60,
        elapsed,
    )


@pytest.fixture
def paced(request: pytest.FixtureRequest):
    """Number the test, log its start, and log a failure if it never finishes.

    Args:
        request: Pytest request for the running test.

    Yields:
        PacedCase: Logger and pacer for the running test.
    """
    global _tests_started
    _tests_started += 1
    case = PacedCase(request, _tests_started)
    yield case
    if not case.closed:
        logger.info(
            "  RESULT FAIL %s — assertion failed. Last response: %s",
            case.name,
            case.last_summary or "<no response yet>",
        )


class TestLongPetstorePets:
    """Pet create, read, update, delete, plus invalid ids and bodies."""

    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_add_pet_for_each_status(self, status, paced, petstore_client, assert_api):
        """POST /pet echoes the pet for each documented status.

        Args:
            status: Pet status sent in the new pet.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload(status=status)
        response = paced.call(
            f"POST /pet name={pet['name']} status={status}",
            lambda: petstore_client.add_pet(pet),
        )

        assert_api.status_code(response, 200)
        assert_json_types(response, Pet)
        assert_api.json_contains(response, "name", pet["name"])
        assert_api.json_contains(response, "status", status)
        assert_api.json_contains(response, "photoUrls", pet["photoUrls"])
        paced.finish(f"created pet {response.json['id']} with status {status}")

    def test_get_pet_by_id(self, paced, petstore_client, assert_api):
        """Create a pet, then GET /pet/{petId} returns that same pet.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload()
        created = paced.call(
            f"POST /pet name={pet['name']}",
            lambda: petstore_client.add_pet(pet),
        )
        assert_api.status_code(created, 200)
        pet_id = created.json["id"]

        fetched = paced.call(
            f"GET /pet/{pet_id}",
            lambda: petstore_client.get_pet(pet_id),
        )
        assert_api.status_code(fetched, 200)
        assert_json_types(fetched, Pet)
        assert fetched.json["id"] == pet_id
        assert fetched.json["name"] == pet["name"]
        paced.finish(f"GET /pet/{pet_id} returned {fetched.json['name']}")

    def test_update_pet(self, paced, petstore_client, assert_api):
        """PUT /pet changes the name and moves the pet to sold.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload(status="available")
        created = paced.call(
            f"POST /pet name={pet['name']}",
            lambda: petstore_client.add_pet(pet),
        )
        assert_api.status_code(created, 200)
        pet_id = created.json["id"]
        updated = {
            **pet,
            "id": pet_id,
            "name": f"updated-{pet['name']}",
            "status": "sold",
        }

        response = paced.call(
            f"PUT /pet id={pet_id} name={updated['name']} status=sold",
            lambda: petstore_client.update_pet(updated),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, Pet)
        assert_api.json_contains(response, "name", updated["name"])
        assert_api.json_contains(response, "status", "sold")
        paced.finish(f"updated pet {pet_id} to sold")

    def test_update_pet_with_form(self, paced, petstore_client, assert_api):
        """POST /pet/{petId} form data updates the name and status.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload()
        created = paced.call(
            f"POST /pet name={pet['name']}",
            lambda: petstore_client.add_pet(pet),
        )
        assert_api.status_code(created, 200)
        pet_id = created.json["id"]
        new_name = f"form-{pet['name']}"

        response = paced.call(
            f"POST /pet/{pet_id} form name={new_name} status=pending",
            lambda: petstore_client.update_pet_with_form(
                pet_id, name=new_name, status="pending"
            ),
        )
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        paced.finish(f"form update accepted for pet {pet_id}")

    def test_delete_pet(self, paced, petstore_client, assert_api):
        """DELETE /pet/{petId} removes the pet; a later GET is 404.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload()
        created = paced.call(
            f"POST /pet name={pet['name']}",
            lambda: petstore_client.add_pet(pet),
        )
        assert_api.status_code(created, 200)
        pet_id = created.json["id"]

        deleted = paced.call(
            f"DELETE /pet/{pet_id}",
            lambda: petstore_client.delete_pet(pet_id),
        )
        assert_api.status_code(deleted, 200)

        missing = paced.call(
            f"GET /pet/{pet_id} after delete",
            lambda: petstore_client.get_pet(pet_id),
        )
        assert_api.status_code(missing, 404)
        assert "not found" in _message(missing).lower()
        paced.finish(f"pet {pet_id} deleted and now 404")

    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_find_pets_by_each_status(self, status, paced, petstore_client, assert_api):
        """GET /pet/findByStatus returns a JSON list for each real status.

        Args:
            status: Pet status used as the search filter.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            f"GET /pet/findByStatus?status={status}",
            lambda: petstore_client.find_pets_by_status(status=status),
        )
        assert_api.status_code(response, 200)
        assert isinstance(response.json, list)
        assert all(isinstance(item, dict) for item in response.json)
        paced.finish(f"status {status} returned {len(response.json)} pets")

    def test_find_pets_by_multiple_statuses(self, paced, petstore_client, assert_api):
        """GET /pet/findByStatus accepts available and pending together.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /pet/findByStatus?status=available&status=pending",
            lambda: _raw_call(
                petstore_client,
                "/pet/findByStatus",
                params={"status": ["available", "pending"]},
            ),
        )
        assert_api.status_code(response, 200)
        assert isinstance(response.json, list)
        paced.finish(f"two statuses returned {len(response.json)} pets")

    def test_find_pets_by_tag(self, paced, petstore_client, assert_api):
        """GET /pet/findByTags?tags=tag1 returns a list (deprecated route).

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /pet/findByTags?tags=tag1",
            lambda: _raw_call(
                petstore_client, "/pet/findByTags", params={"tags": "tag1"}
            ),
        )
        assert_api.status_code(response, 200)
        assert isinstance(response.json, list)
        paced.finish(f"tag1 returned {len(response.json)} pets")

    def test_pet_lifecycle(self, paced, petstore_client, assert_api):
        """Walk one pet through create, read, update, form update, and delete.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        pet = pet_payload(status="pending")
        created = paced.call(
            f"POST /pet name={pet['name']}",
            lambda: petstore_client.add_pet(pet),
        )
        assert_api.status_code(created, 200)
        pet_id = created.json["id"]

        fetched = paced.call(
            f"GET /pet/{pet_id}",
            lambda: petstore_client.get_pet(pet_id),
        )
        assert_api.status_code(fetched, 200)
        assert fetched.json["name"] == pet["name"]

        renamed = {**pet, "id": pet_id, "name": f"life-{pet['name']}", "status": "sold"}
        updated = paced.call(
            f"PUT /pet id={pet_id} status=sold",
            lambda: petstore_client.update_pet(renamed),
        )
        assert_api.status_code(updated, 200)
        assert updated.json["status"] == "sold"

        formed = paced.call(
            f"POST /pet/{pet_id} form status=available",
            lambda: petstore_client.update_pet_with_form(pet_id, status="available"),
        )
        assert_api.status_code(formed, 200)

        deleted = paced.call(
            f"DELETE /pet/{pet_id}",
            lambda: petstore_client.delete_pet(pet_id),
        )
        assert_api.status_code(deleted, 200)
        paced.finish(f"lifecycle finished for pet {pet_id}")

    @pytest.mark.parametrize("status", ["nope", "flying", "not-a-real-status"])
    def test_unknown_status_is_empty(self, status, paced, petstore_client, assert_api):
        """An unknown status filter returns HTTP 200 and an empty list.

        Args:
            status: Status value that is not a real pet status.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            f"GET /pet/findByStatus?status={status}",
            lambda: petstore_client.find_pets_by_status(status=status),
        )
        assert_api.status_code(response, 200)
        assert response.json == []
        paced.finish(f"status {status!r} returned an empty list")

    def test_find_pets_without_status(self, paced, petstore_client, assert_api):
        """GET /pet/findByStatus with no query returns an empty list.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /pet/findByStatus",
            lambda: _raw_call(petstore_client, "/pet/findByStatus"),
        )
        assert_api.status_code(response, 200)
        assert response.json == []
        paced.finish("missing status query returned an empty list")

    @pytest.mark.parametrize("pet_id", [999999999, 0, -1])
    def test_get_missing_pet(self, pet_id, paced, petstore_client, assert_api):
        """GET /pet/{petId} is 404 when that id is not in the store.

        Args:
            pet_id: Pet id that does not exist.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            f"GET /pet/{pet_id}",
            lambda: petstore_client.get_pet(pet_id),
        )
        assert_api.status_code(response, 404)
        assert "not found" in _message(response).lower()
        paced.finish(f"pet id {pet_id} correctly returned 404")

    def test_get_pet_non_numeric_id(self, paced, petstore_client, assert_api):
        """GET /pet/abc is 404 and reports that the id is not a number.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /pet/abc",
            lambda: _raw_call(petstore_client, "/pet/abc"),
        )
        assert_api.status_code(response, 404)
        assert "NumberFormatException" in _body_text(response)
        paced.finish("non-numeric pet id was rejected")

    def test_delete_missing_pet(self, paced, petstore_client, assert_api):
        """DELETE /pet/{petId} is 404 when the pet does not exist.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "DELETE /pet/999999999",
            lambda: petstore_client.delete_pet(999999999),
        )
        assert_api.status_code(response, 404)
        paced.finish("delete of a missing pet returned 404")

    def test_delete_pet_non_numeric_id(self, paced, petstore_client, assert_api):
        """DELETE /pet/abc is 404 and reports that the id is not a number.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "DELETE /pet/abc",
            lambda: _raw_call(petstore_client, "/pet/abc", method="DELETE"),
        )
        assert_api.status_code(response, 404)
        assert "NumberFormatException" in _body_text(response)
        paced.finish("non-numeric delete was rejected")

    def test_add_pet_malformed_json(self, paced, petstore_client, assert_api):
        """POST /pet with a body that is not JSON returns 400 bad input.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "POST /pet body=not-json",
            lambda: _raw_call(petstore_client, "/pet", method="POST", data="not-json"),
        )
        assert_api.status_code(response, 400)
        assert "bad input" in _message(response)
        paced.finish("malformed JSON was rejected with 400")

    def test_add_pet_xml_body(self, paced, petstore_client, assert_api):
        """POST /pet with an unexpected XML element returns 400.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "POST /pet Content-Type=application/xml body=<pet/>",
            lambda: _raw_call(
                petstore_client,
                "/pet",
                method="POST",
                data="<pet></pet>",
                headers={"Content-Type": "application/xml"},
            ),
        )
        assert_api.status_code(response, 400)
        assert "UnmarshalException" in _body_text(response)
        paced.finish("unexpected XML was rejected with 400")


class TestLongPetstoreStore:
    """Inventory and orders. Documented GET ids are 1 through 10."""

    def test_inventory(self, paced, petstore_client, assert_api):
        """GET /store/inventory returns a map of status names to counts.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /store/inventory",
            lambda: petstore_client.get_inventory(),
        )
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert isinstance(response.json, dict)
        assert response.json
        assert all(isinstance(value, int) for value in response.json.values())
        paced.finish(f"inventory has {len(response.json)} status keys")

    @pytest.mark.parametrize("status", ["placed", "approved", "delivered"])
    def test_place_order_for_each_status(
        self, status, paced, petstore_client, assert_api
    ):
        """POST /store/order accepts each documented order status.

        Args:
            status: Order status sent in the new order.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        order = _order(status=status, quantity=2)
        response = paced.call(
            f"POST /store/order id={order['id']} status={status}",
            lambda: petstore_client.place_order(order),
        )
        assert_api.status_code(response, 200)
        assert_api.has_content(response)
        assert response.json["status"] == status
        assert response.json["quantity"] == 2
        assert response.json["complete"] is False
        paced.finish(f"placed order {response.json['id']} status {status}")

    @pytest.mark.parametrize("order_id", list(range(1, 11)))
    def test_get_order_in_valid_id_range(
        self, order_id, paced, petstore_client, assert_api
    ):
        """GET /store/order/{orderId} succeeds for ids 1 through 10.

        Args:
            order_id: Order id inside the documented 1-10 range.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            f"GET /store/order/{order_id}",
            lambda: petstore_client.get_order(order_id),
        )
        assert_api.status_code(response, 200)
        assert response.json["id"] == order_id
        assert isinstance(response.json["complete"], bool)
        assert response.json["status"] in {"placed", "approved", "delivered"}
        paced.finish(
            f"order {order_id} is {response.json['status']} "
            f"complete={response.json['complete']}"
        )

    def test_place_order_then_get(self, paced, petstore_client, assert_api):
        """An order posted with id 6 is the order returned by GET.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        order = _order(status="approved", order_id=6, quantity=4)
        created = paced.call(
            "POST /store/order id=6 status=approved quantity=4",
            lambda: petstore_client.place_order(order),
        )
        assert_api.status_code(created, 200)
        assert created.json["id"] == 6

        fetched = paced.call(
            "GET /store/order/6",
            lambda: petstore_client.get_order(6),
        )
        assert_api.status_code(fetched, 200)
        assert fetched.json["id"] == 6
        assert fetched.json["petId"] == order["petId"]
        assert fetched.json["quantity"] == 4
        assert fetched.json["status"] == "approved"
        paced.finish("order 6 round-tripped through GET")

    @pytest.mark.parametrize("order_id", [0, 11, -5, 99999])
    def test_get_order_not_found(self, order_id, paced, petstore_client, assert_api):
        """GET /store/order/{orderId} is 404 outside the documented 1-10 range.

        Args:
            order_id: Order id outside the documented 1-10 range.
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            f"GET /store/order/{order_id}",
            lambda: petstore_client.get_order(order_id),
        )
        assert_api.status_code(response, 404)
        assert "not found" in _message(response).lower()
        paced.finish(f"order id {order_id} correctly returned 404")

    def test_get_order_non_numeric_id(self, paced, petstore_client, assert_api):
        """GET /store/order/abc is 404 and reports that the id is not a number.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /store/order/abc",
            lambda: _raw_call(petstore_client, "/store/order/abc"),
        )
        assert_api.status_code(response, 404)
        assert "NumberFormatException" in _body_text(response)
        paced.finish("non-numeric order id was rejected")

    def test_place_order_bad_id_type(self, paced, petstore_client, assert_api):
        """POST /store/order with a non-numeric id returns 500 on this demo.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        bad_order = {
            "id": "nope",
            "petId": 1,
            "quantity": 1,
            "status": "placed",
            "complete": False,
        }
        response = paced.call(
            "POST /store/order id=nope",
            lambda: petstore_client.place_order(bad_order),
        )
        assert_api.status_code(response, 500)
        paced.finish("non-numeric order id returned 500")

    def test_delete_missing_order(self, paced, petstore_client, assert_api):
        """DELETE /store/order/11 is 404 because that id is not stored.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "DELETE /store/order/11",
            lambda: petstore_client.delete_order(11),
        )
        assert_api.status_code(response, 404)
        assert "not found" in _message(response).lower()
        paced.finish("delete of missing order 11 returned 404")

    def test_delete_order_non_numeric_id(self, paced, petstore_client, assert_api):
        """DELETE /store/order/abc is 404 and reports that the id is not a number.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "DELETE /store/order/abc",
            lambda: _raw_call(petstore_client, "/store/order/abc", method="DELETE"),
        )
        assert_api.status_code(response, 404)
        assert "NumberFormatException" in _body_text(response)
        paced.finish("non-numeric order delete was rejected")


class TestLongPetstoreUsers:
    """User create, read, update, login, logout, and delete."""

    def test_create_user(self, paced, petstore_client, assert_api):
        """POST /user acknowledges a new user.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        response = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)
        paced.finish(f"created user {user['username']}")

    def test_get_user_by_name(self, paced, petstore_client, assert_api):
        """GET /user/{username} returns the user that was just created.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        created = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(created, 200)

        fetched = paced.call(
            f"GET /user/{user['username']}",
            lambda: petstore_client.get_user(user["username"]),
        )
        assert_api.status_code(fetched, 200)
        assert_json_types(fetched, User)
        assert_api.json_contains(fetched, "username", user["username"])
        assert_api.json_contains(fetched, "email", user["email"])
        paced.finish(f"fetched user {user['username']}")

    def test_update_user(self, paced, petstore_client, assert_api):
        """PUT /user/{username} changes the first name seen on the next GET.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        created = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(created, 200)

        updated = {**user, "firstName": "Updated", "lastName": "Name"}
        response = paced.call(
            f"PUT /user/{user['username']} firstName=Updated",
            lambda: petstore_client.update_user(user["username"], updated),
        )
        assert_api.status_code(response, 200)

        fetched = paced.call(
            f"GET /user/{user['username']}",
            lambda: petstore_client.get_user(user["username"]),
        )
        assert_api.status_code(fetched, 200)
        assert fetched.json["firstName"] == "Updated"
        assert fetched.json["lastName"] == "Name"
        paced.finish(f"updated user {user['username']}")

    def test_login_user(self, paced, petstore_client, assert_api):
        """GET /user/login returns a session message for a created user.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        created = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(created, 200)

        response = paced.call(
            f"GET /user/login username={user['username']}",
            lambda: petstore_client.login_user(user["username"], user["password"]),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)
        assert "logged in user session" in _message(response)
        paced.finish(f"login session opened for {user['username']}")

    def test_logout_user(self, paced, petstore_client, assert_api):
        """GET /user/logout returns the demo's ok message.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /user/logout",
            lambda: petstore_client.logout_user(),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)
        assert _message(response) == "ok"
        paced.finish("logout returned ok")

    def test_delete_user(self, paced, petstore_client, assert_api):
        """DELETE /user/{username} removes the user; the next GET is 404.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        created = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(created, 200)

        deleted = paced.call(
            f"DELETE /user/{user['username']}",
            lambda: petstore_client.delete_user(user["username"]),
        )
        assert_api.status_code(deleted, 200)

        missing = paced.call(
            f"GET /user/{user['username']}",
            lambda: petstore_client.get_user(user["username"]),
        )
        assert_api.status_code(missing, 404)
        assert "not found" in _message(missing).lower()
        paced.finish(f"user {user['username']} deleted and now 404")

    def test_create_users_with_list(self, paced, petstore_client, assert_api):
        """POST /user/createWithList accepts an array of users.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        users = [user_payload(), user_payload()]
        response = paced.call(
            "POST /user/createWithList count=2",
            lambda: _raw_call(
                petstore_client,
                "/user/createWithList",
                method="POST",
                data=json.dumps(users),
            ),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)
        assert _message(response) == "ok"
        paced.finish(
            f"created list users {users[0]['username']} and {users[1]['username']}"
        )

    def test_create_users_with_array(self, paced, petstore_client, assert_api):
        """POST /user/createWithArray accepts an array of users.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        users = [user_payload(), user_payload()]
        response = paced.call(
            "POST /user/createWithArray count=2",
            lambda: _raw_call(
                petstore_client,
                "/user/createWithArray",
                method="POST",
                data=json.dumps(users),
            ),
        )
        assert_api.status_code(response, 200)
        assert_json_types(response, ApiResponse)
        assert _message(response) == "ok"
        paced.finish(
            f"created array users {users[0]['username']} and {users[1]['username']}"
        )

    def test_user_lifecycle(self, paced, petstore_client, assert_api):
        """Create a user, update them, log in, then delete them.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        user = user_payload()
        created = paced.call(
            f"POST /user username={user['username']}",
            lambda: petstore_client.create_user(user),
        )
        assert_api.status_code(created, 200)

        updated = {**user, "firstName": "Lifecycle"}
        changed = paced.call(
            f"PUT /user/{user['username']}",
            lambda: petstore_client.update_user(user["username"], updated),
        )
        assert_api.status_code(changed, 200)

        logged_in = paced.call(
            f"GET /user/login username={user['username']}",
            lambda: petstore_client.login_user(user["username"], user["password"]),
        )
        assert_api.status_code(logged_in, 200)
        assert "logged in user session" in _message(logged_in)

        deleted = paced.call(
            f"DELETE /user/{user['username']}",
            lambda: petstore_client.delete_user(user["username"]),
        )
        assert_api.status_code(deleted, 200)
        paced.finish(f"lifecycle finished for {user['username']}")

    def test_get_unknown_user(self, paced, petstore_client, assert_api):
        """GET /user/{username} is 404 when that username was never created.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        username = "missing-user-long-suite"
        response = paced.call(
            f"GET /user/{username}",
            lambda: petstore_client.get_user(username),
        )
        assert_api.status_code(response, 404)
        assert "not found" in _message(response).lower()
        paced.finish(f"{username} correctly returned 404")

    def test_delete_unknown_user(self, paced, petstore_client, assert_api):
        """DELETE /user/{username} is 404 when that username does not exist.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        username = "missing-user-long-suite-delete"
        response = paced.call(
            f"DELETE /user/{username}",
            lambda: petstore_client.delete_user(username),
        )
        assert_api.status_code(response, 404)
        paced.finish(f"delete of {username} returned 404")

    def test_login_blank_credentials(self, paced, petstore_client, assert_api):
        """A blank username and password still opens a session on the public demo.

        Args:
            paced: Logs the test and paces it to its time slice.
            petstore_client: Unauthenticated Petstore API client.
            assert_api: Assertion helpers for API responses.
        """
        response = paced.call(
            "GET /user/login username= password=",
            lambda: petstore_client.login_user("", ""),
        )
        assert_api.status_code(response, 200)
        assert "logged in user session" in _message(response)
        paced.finish("blank login was accepted by the public demo")
