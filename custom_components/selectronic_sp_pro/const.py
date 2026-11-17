"""Constants for the Selectronic SP PRO integration."""

from __future__ import annotations

DOMAIN = "selectronic_sp_pro"
DEFAULT_NAME = "Selectronic SP PRO"
DEFAULT_SCAN_INTERVAL = 10
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300

CONF_HOST = "host"
CONF_DEVICE_ID = "device_id"
CONF_USE_HTTPS = "use_https"
CONF_VERIFY_SSL = "verify_ssl"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_OFF_GRID_MODE = "off_grid_mode"

ATTR_DEVICE_NAME = "device_name"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_SHORT_ID = "short_id"
ATTR_ITEM_COUNT = "item_count"
ATTR_LAST_UPDATED = "last_updated"

FAULT_CODES: dict[int, str] = {
    0: "No Fault",
    1: "Over Temperature",
    2: "Battery Low",
    3: "Battery High",
    4: "AC Overload",
    5: "Short Circuit",
    6: "Generator Fault",
    7: "Grid Fault",
    8: "Internal Hardware Fault",
}

GEN_STATUS_MAP: dict[int, str] = {
    0: "Stopped",
    1: "Starting",
    2: "Running",
    3: "Cooling Down",
    4: "Fault / Lockout",
}
