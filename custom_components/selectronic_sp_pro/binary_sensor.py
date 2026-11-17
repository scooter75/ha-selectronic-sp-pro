"""Binary sensor platform for Selectronic SP PRO."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, CONF_HOST, DEFAULT_NAME, DOMAIN
from .coordinator import SelectronicDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SelectronicBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a Selectronic SP PRO binary sensor."""

    item_key: str
    is_on_fn: Callable[[Any], bool]


BINARY_SENSOR_DESCRIPTIONS: tuple[SelectronicBinarySensorDescription, ...] = (
    SelectronicBinarySensorDescription(
        key="inverter_fault",
        item_key="fault_code",
        name="Inverter Fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda val: int(val) != 0,
    ),
    SelectronicBinarySensorDescription(
        key="generator_running",
        item_key="gen_status",
        name="Generator Running",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda val: int(val) in (1, 2),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Selectronic SP PRO binary sensors."""
    coordinator: SelectronicDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    items = coordinator.data.get("items", {})

    entities = [
        SelectronicSpProBinarySensor(coordinator, entry, desc)
        for desc in BINARY_SENSOR_DESCRIPTIONS
        if desc.item_key in items
    ]
    async_add_entities(entities)


class SelectronicSpProBinarySensor(
    CoordinatorEntity[SelectronicDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a Selectronic SP PRO binary sensor."""

    entity_description: SelectronicBinarySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SelectronicDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SelectronicBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        device_id = entry.data.get(CONF_DEVICE_ID, entry.entry_id)

        self._attr_unique_id = f"{device_id}_{description.key}"

        meta = coordinator.data.get("meta", {})
        dev_name = coordinator.data.get("device", {}).get("name") or DEFAULT_NAME
        serial_num = meta.get("serialnum")

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=dev_name,
            manufacturer="Selectronic Australia",
            model="SP PRO Series",
            serial_number=str(serial_num) if serial_num else None,
            configuration_url=f"http://{entry.data[CONF_HOST]}",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        raw_val = self.coordinator.data.get("items", {}).get(
            self.entity_description.item_key
        )
        if raw_val is None:
            return None
        try:
            return self.entity_description.is_on_fn(raw_val)
        except (ValueError, TypeError):
            return False
