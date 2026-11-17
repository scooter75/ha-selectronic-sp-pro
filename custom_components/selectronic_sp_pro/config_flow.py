"""Config flow for Selectronic SP PRO integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    SelectronicApiClient,
    SelectronicApiError,
    SelectronicConnectionError,
    SelectronicDeviceDiscoveryError,
)
from .const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_OFF_GRID_MODE,
    CONF_SCAN_INTERVAL,
    CONF_USE_HTTPS,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class SelectronicConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Selectronic SP PRO."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            device_id = user_input.get(CONF_DEVICE_ID, "").strip() or None
            use_https = user_input.get(CONF_USE_HTTPS, False)
            verify_ssl = user_input.get(CONF_VERIFY_SSL, False)

            session = async_get_clientsession(self.hass)
            client = SelectronicApiClient(
                session=session,
                host=host,
                device_id=device_id,
                use_https=use_https,
                verify_ssl=verify_ssl,
            )

            try:
                payload = await client.async_get_point_data()
                discovered_id = client.device_id
                if not discovered_id:
                    errors["base"] = "no_devices_found"
                else:
                    await self.async_set_unique_id(discovered_id)
                    self._abort_if_unique_id_configured()

                    device_name = payload.get("device", {}).get("name") or DEFAULT_NAME
                    serial_num = client.device_meta.get("serialnum", "")
                    title = f"{device_name} ({serial_num})" if serial_num else f"{device_name} ({client.host})"

                    data = {
                        CONF_HOST: client.host,
                        CONF_DEVICE_ID: discovered_id,
                        CONF_USE_HTTPS: use_https,
                        CONF_VERIFY_SSL: verify_ssl,
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        CONF_OFF_GRID_MODE: user_input.get(CONF_OFF_GRID_MODE, False),
                    }
                    return self.async_create_entry(title=title, data=data)

            except SelectronicDeviceDiscoveryError:
                errors["base"] = "no_devices_found"
            except SelectronicConnectionError:
                errors["base"] = "cannot_connect"
            except SelectronicApiError:
                errors["base"] = "invalid_response"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error setting up Selectronic SP PRO")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_DEVICE_ID, default=""): str,
                vol.Optional(CONF_USE_HTTPS, default=False): bool,
                vol.Optional(CONF_VERIFY_SSL, default=False): bool,
                vol.Optional(CONF_OFF_GRID_MODE, default=False): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return SelectronicOptionsFlowHandler(config_entry)


class SelectronicOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Selectronic SP PRO."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_off_grid = self.config_entry.options.get(
            CONF_OFF_GRID_MODE,
            self.config_entry.data.get(CONF_OFF_GRID_MODE, False),
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
                vol.Optional(CONF_OFF_GRID_MODE, default=current_off_grid): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
