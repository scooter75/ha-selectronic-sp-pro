# Selectronic SP PRO for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/scooter75/ha-selectronic-sp-pro.svg)](https://github.com/scooter75/ha-selectronic-sp-pro/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <img src="custom_components/selectronic_sp_pro/brand/logo.png" alt="Selectronic SP PRO Logo" width="380"/>
</p>

A native, local-polling Home Assistant integration for **Selectronic SP PRO** Series Inverter Chargers via the local **Select.live** gateway. Designed for seamless compatibility with the Home Assistant **Energy Dashboard** and HACS / Home Assistant Marketplace.

---

## Features

- **100% Local Polling**: Communicates directly with your Select.live gateway on your local LAN (`http://<local_ip>/cgi-bin/solarmonweb/devices/<device_id>/point`)—no cloud dependency required once configured.
- **UI Configuration & Auto-Discovery**: Add via **Settings → Devices & Services**. Automatically queries `/cgi-bin/solarmonweb/devices/` to detect your SP PRO inverter's 32-character Device ID and serial number.
- **Full Energy Dashboard Support**: Exposes cumulative `TOTAL_INCREASING` Watt-hour (`Wh`) counters (`solar_wh_total`, `load_wh_total`, `battery_in_wh_total`, `battery_out_wh_total`, `grid_in_wh_total`, `grid_out_wh_total`) that prevent midnight reset spikes.
- **Off-Grid & On-Grid Support**: Optional **Off-Grid Mode** relabels AC grid input sensors as Generator / AC Input sensors for off-grid installations.
- **Diagnostics & Binary Sensors**: Dedicated binary sensors for **Inverter Fault** and **Generator Running**, plus human-readable fault and generator status text sensors.
- **Bundled Brand Assets**: Includes high-DPI local brand icons and logos (`brand/icon.png`, `brand/logo.png`) so Home Assistant displays the Selectronic emblem natively in the UI.

---

## Supported Hardware

- **Selectronic SP PRO Series** (SPMC, SPLC, Series 1, Series 2, Series 2i)
- Connected to your local network via a **Select.live** monitoring device (Firmware supporting the `solarmonweb` local JSON API).

---

## Installation

### Option 1: HACS / Home Assistant Marketplace (Recommended)

1. Open **HACS** (or **Marketplace** in Home Assistant 2026.11+) in your Home Assistant sidebar.
2. Click the three-dots menu (`⋮`) in the top-right corner and select **Custom repositories**.
3. Enter the repository URL:
   ```text
   https://github.com/scooter75/ha-selectronic-sp-pro
   ```
4. Select **Integration** as the category and click **Add**.
5. Search for **Selectronic SP PRO**, click **Download**, and restart Home Assistant when prompted.

### Option 2: Manual Installation

1. Download the latest release archive from [GitHub Releases](https://github.com/scooter75/ha-selectronic-sp-pro/releases).
2. Copy the `custom_components/selectronic_sp_pro` folder into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. Navigate to **Settings → Devices & Services**.
2. Click **+ Add Integration** and search for **Selectronic SP PRO**.
3. Fill in the connection parameters:
   - **Select.live Local IP Address / Hostname**: The static LAN IP address of your Select.live gateway (e.g., `192.168.1.50`). *Tip: Assign a DHCP reservation on your router so this IP never changes.*
   - **Device ID (Optional)**: Leave blank to let the integration auto-discover your inverter. If auto-discovery fails on older firmware, paste your 32-character hex Device ID manually.
   - **Off-Grid Mode**: Enable if your SP PRO is off-grid and uses the AC input port for a backup generator.
   - **Polling Interval**: Defaults to `10` seconds (configurable between `5` and `300` seconds).

---

## Available Entities

> **Note:** Entities are dynamically created based on the telemetry keys reported by your specific SP PRO firmware and system configuration.

### Sensors

| Entity Key | Friendly Name | Unit | Device Class | State Class |
| :--- | :--- | :---: | :---: | :---: |
| `battery_soc` | Battery State of Charge | `%` | `battery` | `measurement` |
| `battery_w` | Battery Power | `W` | `power` | `measurement` |
| `battery_charge_w` | Battery Charge Power *(derived)* | `W` | `power` | `measurement` |
| `battery_discharge_w` | Battery Discharge Power *(derived)* | `W` | `power` | `measurement` |
| `battery_v` | Battery Voltage | `V` | `voltage` | `measurement` |
| `battery_a` | Battery Current | `A` | `current` | `measurement` |
| `battery_temp` | Battery Temperature | `°C` | `temperature` | `measurement` |
| `battery_in_wh_today` | Battery Energy Charged Today | `Wh` | `energy` | `total_increasing` |
| `battery_out_wh_today` | Battery Energy Discharged Today | `Wh` | `energy` | `total_increasing` |
| `battery_in_wh_total` | Battery Energy Charged Total | `Wh` | `energy` | `total_increasing` |
| `battery_out_wh_total` | Battery Energy Discharged Total | `Wh` | `energy` | `total_increasing` |
| `solar_w` | Solar Power | `W` | `power` | `measurement` |
| `solar_wh_today` | Solar Energy Today | `Wh` | `energy` | `total_increasing` |
| `solar_wh_total` | Solar Energy Total | `Wh` | `energy` | `total_increasing` |
| `load_w` | Load Power | `W` | `power` | `measurement` |
| `load_wh_today` | Load Energy Today | `Wh` | `energy` | `total_increasing` |
| `load_wh_total` | Load Energy Total | `Wh` | `energy` | `total_increasing` |
| `grid_w` | Grid Power / Generator AC Input Power | `W` | `power` | `measurement` |
| `grid_import_w` | Grid Import Power *(derived)* | `W` | `power` | `measurement` |
| `grid_export_w` | Grid Export Power *(derived)* | `W` | `power` | `measurement` |
| `grid_in_wh_today` | Grid Energy Imported Today | `Wh` | `energy` | `total_increasing` |
| `grid_in_wh_total` | Grid Energy Imported Total | `Wh` | `energy` | `total_increasing` |
| `grid_out_wh_today` | Grid Energy Exported Today | `Wh` | `energy` | `total_increasing` |
| `grid_out_wh_total` | Grid Energy Exported Total | `Wh` | `energy` | `total_increasing` |
| `ac_out_v` | AC Output Voltage | `V` | `voltage` | `measurement` |
| `ac_out_hz` | AC Output Frequency | `Hz` | `frequency` | `measurement` |
| `inverter_temp` | Inverter Temperature | `°C` | `temperature` | `measurement` |
| `gen_status` | Generator Status | — | — | — |
| `fault_code` | Fault Status | — | — | — |
| `fault_code_raw` | Fault Code | — | — | — |

### Binary Sensors

| Entity Key | Friendly Name | Device Class | Condition |
| :--- | :--- | :---: | :--- |
| `inverter_fault` | Inverter Fault | `problem` | `fault_code != 0` |
| `generator_running` | Generator Running | `running` | `gen_status in (1, 2)` |

---

## Home Assistant Energy Dashboard Setup

To configure the built-in **Energy Dashboard** (**Settings → Dashboards → Energy**), always select the **`*_total`** lifetime sensors rather than `*_today`:

- **Solar Panels**: `sensor.selectronic_sp_pro_solar_energy_total`
- **Home Battery Storage**:
  - Energy going in: `sensor.selectronic_sp_pro_battery_energy_charged_total`
  - Energy coming out: `sensor.selectronic_sp_pro_battery_energy_discharged_total`
- **Electricity Grid** *(or Off-Grid Generator)*:
  - Grid consumption: `sensor.selectronic_sp_pro_grid_energy_imported_total` (or `Generator Energy Total` in Off-Grid Mode)
  - Return to grid: `sensor.selectronic_sp_pro_grid_energy_exported_total`

---

## Troubleshooting

- **Cannot Connect**: Ensure your Select.live gateway has a strong Wi-Fi or Ethernet connection and is reachable via `http://<IP>/cgi-bin/solarmonweb/devices/` from a browser on the same network.
- **No Devices Found**: Open `http://<IP>/cgi-bin/solarmonweb/devices/` in your browser. If it returns an empty array `[]`, verify that the Select.live serial/RS-485 cable is firmly seated in the SP PRO communications port.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
