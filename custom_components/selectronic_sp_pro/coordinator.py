"""DataUpdateCoordinator for Selectronic SP PRO."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SelectronicApiClient, SelectronicApiError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SelectronicDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Selectronic SP PRO telemetry."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: SelectronicApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        scan_seconds = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_seconds),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest point data from Selectronic SP PRO."""
        try:
            payload = await self.client.async_get_point_data()
        except SelectronicApiError as err:
            raise UpdateFailed(f"Error communicating with Selectronic SP PRO: {err}") from err

        items: dict[str, Any] = payload.get("items", {})
        device_info: dict[str, Any] = payload.get("device", {})

        # Compute helpful derived metrics if raw fields exist
        derived: dict[str, Any] = {}
        bat_w = items.get("battery_w")
        if isinstance(bat_w, (int, float)):
            # Positive battery_w in Select.live typically indicates charging or discharging depending on firmware;
            # expose split charge/discharge power helpers for convenience
            derived["battery_charge_w"] = max(0.0, float(bat_w))
            derived["battery_discharge_w"] = max(0.0, float(-bat_w))

        grid_w = items.get("grid_w")
        if isinstance(grid_w, (int, float)):
            derived["grid_import_w"] = max(0.0, float(grid_w))
            derived["grid_export_w"] = max(0.0, float(-grid_w))

        return {
            "device": device_info,
            "item_count": payload.get("item_count", len(items)),
            "items": items,
            "derived": derived,
            "meta": self.client.device_meta,
        }
