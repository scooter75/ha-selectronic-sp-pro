"""Async API client for Selectronic SP PRO via Select.live local gateway."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SelectronicApiError(Exception):
    """Base exception for Selectronic API errors."""


class SelectronicConnectionError(SelectronicApiError):
    """Exception raised when unable to connect to the Select.live gateway."""


class SelectronicDeviceDiscoveryError(SelectronicApiError):
    """Exception raised when device ID cannot be auto-discovered."""


class SelectronicApiClient:
    """Async client to communicate with a local Select.live gateway."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        device_id: str | None = None,
        use_https: bool = False,
        verify_ssl: bool = False,
        timeout: int = 10,
    ) -> None:
        """Initialize the Selectronic API client."""
        self._session = session
        self._host = host.strip().rstrip("/")
        # Strip scheme if user accidentally pasted full URL
        if self._host.startswith("http://"):
            self._host = self._host[7:]
            use_https = False
        elif self._host.startswith("https://"):
            self._host = self._host[8:]
            use_https = True

        self._device_id = device_id.strip() if device_id else None
        self._scheme = "https" if use_https else "http"
        self._verify_ssl = verify_ssl
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._device_meta: dict[str, Any] = {}

    @property
    def host(self) -> str:
        """Return configured host."""
        return self._host

    @property
    def device_id(self) -> str | None:
        """Return configured or discovered device ID."""
        return self._device_id

    @property
    def device_meta(self) -> dict[str, Any]:
        """Return discovered device metadata."""
        return self._device_meta

    @property
    def base_url(self) -> str:
        """Return base solarmonweb URL."""
        return f"{self._scheme}://{self._host}/cgi-bin/solarmonweb"

    async def async_discover_devices(self) -> list[dict[str, Any]]:
        """Query /cgi-bin/solarmonweb/devices/ to auto-discover attached SP PRO inverters."""
        url = f"{self.base_url}/devices/"
        try:
            async with self._session.get(
                url,
                timeout=self._timeout,
                ssl=self._verify_ssl if self._scheme == "https" else None,
            ) as response:
                if response.status != 200:
                    raise SelectronicConnectionError(
                        f"HTTP {response.status} returned from {url}"
                    )
                data = await response.json(content_type=None)
                if not isinstance(data, list) or len(data) == 0:
                    raise SelectronicDeviceDiscoveryError(
                        "No Selectronic devices found at gateway endpoint"
                    )
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise SelectronicConnectionError(
                f"Error connecting to Select.live gateway at {url}: {err}"
            ) from err
        except ValueError as err:
            raise SelectronicApiError(
                f"Invalid JSON received during device discovery: {err}"
            ) from err

    async def async_get_point_data(self) -> dict[str, Any]:
        """Fetch live telemetry from /cgi-bin/solarmonweb/devices/<device_id>/point."""
        if not self._device_id:
            devices = await self.async_discover_devices()
            first_dev = devices[0]
            self._device_id = first_dev.get("id")
            self._device_meta = first_dev
            if not self._device_id:
                raise SelectronicDeviceDiscoveryError(
                    "Discovered device entry missing 'id' field"
                )

        url = f"{self.base_url}/devices/{self._device_id}/point"
        try:
            async with self._session.get(
                url,
                timeout=self._timeout,
                ssl=self._verify_ssl if self._scheme == "https" else None,
            ) as response:
                if response.status != 200:
                    raise SelectronicConnectionError(
                        f"HTTP {response.status} returned from {url}"
                    )
                payload = await response.json(content_type=None)
                if not isinstance(payload, dict) or "items" not in payload:
                    raise SelectronicApiError(
                        "Unexpected payload structure: missing 'items' dictionary"
                    )
                return payload
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise SelectronicConnectionError(
                f"Failed to poll Selectronic SP PRO at {url}: {err}"
            ) from err
        except ValueError as err:
            raise SelectronicApiError(
                f"Invalid JSON payload from SP PRO: {err}"
            ) from err
