"""Shared base for domain-specific API clients."""

from typing import Any

from .API_Call import API


class BaseAPIClient:
    """
    Common URL, header, auth, and SSL wiring for domain clients.

    Subclasses add endpoint methods and may override ``_auth_headers``
    for header-based auth (API keys, bearer tokens, etc.).
    """

    def __init__(
        self,
        base_url: str,
        *,
        username: str = "",
        password: str = "",
        verify_ssl: bool = True,
        cert_path: str | None = None,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.cert_path = cert_path
        self.default_headers = default_headers or {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _auth_headers(self) -> dict[str, str]:
        """Extra headers for auth. Override in subclasses (e.g. api_key)."""
        return {}

    def _create_api_instance(
        self,
        endpoint: str,
        method: str = "GET",
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> API:
        """Build a configured ``API`` instance (does not call the network)."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = self.default_headers.copy()
        request_headers.update(self._auth_headers())
        if headers:
            request_headers.update(headers)

        return API(
            address=url,
            method=method.upper(),
            data=data if data is not None else "",
            header=request_headers,
            params=params or "",
            user=self.username,
            password=self.password,
            verify_ssl=self.verify_ssl,
            cert_path=self.cert_path,
        )
