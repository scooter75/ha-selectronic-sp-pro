"""Sensor platform for Selectronic SP PRO."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    CONF_HOST,
    CONF_OFF_GRID_MODE,
    DEFAULT_NAME,
    DOMAIN,
    FAULT_CODES,
    GEN_STATUS_MAP,
)
from .coordinator import SelectronicDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SelectronicSensorDescription(SensorEntityDescription):
    """Describes a Selectronic SP PRO sensor entity."""

    item_key: str
    source_dict: str = "items"  # "items" or "derived"
    precision: int | None = 2
    value_fn: Callable[[Any], Any] | None = None
    off_grid_name: str | None = None


SENSOR_DESCRIPTIONS: tuple[SelectronicSensorDescription, ...] = (
    # Battery Sensors
    SelectronicSensorDescription(
        key="battery_soc",
        item_key="battery_soc",
        name="Battery State of Charge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_w",
        item_key="battery_w",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_charge_w",
        item_key="battery_charge_w",
        source_dict="derived",
        name="Battery Charge Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_discharge_w",
        item_key="battery_discharge_w",
        source_dict="derived",
        name="Battery Discharge Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_v",
        item_key="battery_v",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    SelectronicSensorDescription(
        key="battery_a",
        item_key="battery_a",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    SelectronicSensorDescription(
        key="battery_temp",
        item_key="battery_temp",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_in_wh_today",
        item_key="battery_in_wh_today",
        name="Battery Energy Charged Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_out_wh_today",
        item_key="battery_out_wh_today",
        name="Battery Energy Discharged Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_in_wh_total",
        item_key="battery_in_wh_total",
        name="Battery Energy Charged Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="battery_out_wh_total",
        item_key="battery_out_wh_total",
        name="Battery Energy Discharged Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    # Solar Sensors
    SelectronicSensorDescription(
        key="solar_w",
        item_key="solar_w",
        name="Solar Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="solar_wh_today",
        item_key="solar_wh_today",
        name="Solar Energy Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="solar_wh_total",
        item_key="solar_wh_total",
        name="Solar Energy Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    # Load Sensors
    SelectronicSensorDescription(
        key="load_w",
        item_key="load_w",
        name="Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="load_wh_today",
        item_key="load_wh_today",
        name="Load Energy Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="load_wh_total",
        item_key="load_wh_total",
        name="Load Energy Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    # Grid / Generator AC Source Sensors
    SelectronicSensorDescription(
        key="grid_w",
        item_key="grid_w",
        name="Grid Power",
        off_grid_name="Generator / AC Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_import_w",
        item_key="grid_import_w",
        source_dict="derived",
        name="Grid Import Power",
        off_grid_name="Generator Import Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_export_w",
        item_key="grid_export_w",
        source_dict="derived",
        name="Grid Export Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_in_wh_today",
        item_key="grid_in_wh_today",
        name="Grid Energy Imported Today",
        off_grid_name="Generator Energy Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_in_wh_total",
        item_key="grid_in_wh_total",
        name="Grid Energy Imported Total",
        off_grid_name="Generator Energy Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_out_wh_today",
        item_key="grid_out_wh_today",
        name="Grid Energy Exported Today",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="grid_out_wh_total",
        item_key="grid_out_wh_total",
        name="Grid Energy Exported Total",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="ac_out_v",
        item_key="ac_out_v",
        name="AC Output Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    SelectronicSensorDescription(
        key="ac_out_hz",
        item_key="ac_out_hz",
        name="AC Output Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    SelectronicSensorDescription(
        key="inverter_temp",
        item_key="inverter_temp",
        name="Inverter Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        precision=1,
    ),
    # Status & Diagnostics
    SelectronicSensorDescription(
        key="gen_status",
        item_key="gen_status",
        name="Generator Status",
        icon="mdi:engine",
        precision=None,
        value_fn=lambda val: GEN_STATUS_MAP.get(int(val), f"Unknown ({val})")
        if val is not None
        else None,
    ),
    SelectronicSensorDescription(
        key="fault_code",
        item_key="fault_code",
        name="Fault Status",
        icon="mdi:alert-circle-outline",
        precision=None,
        value_fn=lambda val: FAULT_CODES.get(int(val), f"Fault Code {val}")
        if val is not None
        else None,
    ),
    SelectronicSensorDescription(
        key="fault_code_raw",
        item_key="fault_code",
        name="Fault Code",
        icon="mdi:numeric",
        precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Selectronic SP PRO sensors based on a config entry."""
    coordinator: SelectronicDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    off_grid_mode: bool = entry.options.get(
        CONF_OFF_GRID_MODE, entry.data.get(CONF_OFF_GRID_MODE, False)
    )

    items = coordinator.data.get("items", {})
    derived = coordinator.data.get("derived", {})

    entities: list[SelectronicSpProSensor] = []
    for description in SENSOR_DESCRIPTIONS:
        source = derived if description.source_dict == "derived" else items
        # Only create entities for keys present in the inverter's telemetry feed
        if description.item_key in source:
            entities.append(
                SelectronicSpProSensor(coordinator, entry, description, off_grid_mode)
            )

    async_add_entities(entities)


class SelectronicSpProSensor(
    CoordinatorEntity[SelectronicDataUpdateCoordinator], SensorEntity
):
    """Representation of a Selectronic SP PRO sensor."""

    entity_description: SelectronicSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SelectronicDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SelectronicSensorDescription,
        off_grid_mode: bool,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        device_id = entry.data.get(CONF_DEVICE_ID, entry.entry_id)

        if off_grid_mode and description.off_grid_name:
            self._attr_name = description.off_grid_name

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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        source = (
            self.coordinator.data.get("derived", {})
            if self.entity_description.source_dict == "derived"
            else self.coordinator.data.get("items", {})
        )
        raw_val = source.get(self.entity_description.item_key)
        if raw_val is None:
            return None

        if self.entity_description.value_fn is not None:
            try:
                return self.entity_description.value_fn(raw_val)
            except (ValueError, TypeError):
                return raw_val

        if isinstance(raw_val, (int, float)) and self.entity_description.precision is not None:
            if self.entity_description.precision == 0:
                return int(round(raw_val))
            return round(float(raw_val), self.entity_description.precision)

        return raw_val
