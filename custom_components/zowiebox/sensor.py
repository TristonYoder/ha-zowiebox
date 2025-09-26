"""Sensor platform for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zowiebox sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensors for each device
    sensors = []
    if coordinator.data and "devices" in coordinator.data:
        for device in coordinator.data["devices"]:
            device_id = device.get("id")
            device_name = device.get("name", f"Device {device_id}")
            device_type = device.get("type", "unknown")
            
            # Create appropriate sensors based on device type
            if device_type == "sensor":
                sensors.append(ZowieboxSensor(coordinator, device_id, device_name, device))
            elif device_type == "light":
                # Light devices might have brightness, color temperature sensors
                if "brightness" in device.get("capabilities", []):
                    sensors.append(ZowieboxBrightnessSensor(coordinator, device_id, device_name, device))
                if "color_temp" in device.get("capabilities", []):
                    sensors.append(ZowieboxColorTempSensor(coordinator, device_id, device_name, device))
            elif device_type == "switch":
                # Switch devices might have power consumption sensors
                if "power" in device.get("capabilities", []):
                    sensors.append(ZowieboxPowerSensor(coordinator, device_id, device_name, device))

    async_add_entities(sensors)


class ZowieboxSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Zowiebox sensor."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{name} Status"
        self._attr_unique_id = f"{device_id}_status"
        self._device = device

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("name", f"Device {self._device_id}"),
            "manufacturer": MANUFACTURER,
            "model": self._device.get("model", "Unknown"),
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("status", "unknown")
        
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return None


class ZowieboxBrightnessSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Zowiebox brightness sensor."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the brightness sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{name} Brightness"
        self._attr_unique_id = f"{device_id}_brightness"
        self._device = device

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("name", f"Device {self._device_id}"),
            "manufacturer": MANUFACTURER,
            "model": self._device.get("model", "Unknown"),
        }

    @property
    def native_value(self) -> int | None:
        """Return the brightness value."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("brightness")
        
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "%"


class ZowieboxColorTempSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Zowiebox color temperature sensor."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the color temperature sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{name} Color Temperature"
        self._attr_unique_id = f"{device_id}_color_temp"
        self._device = device

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("name", f"Device {self._device_id}"),
            "manufacturer": MANUFACTURER,
            "model": self._device.get("model", "Unknown"),
        }

    @property
    def native_value(self) -> int | None:
        """Return the color temperature value."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("color_temp")
        
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "K"


class ZowieboxPowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Zowiebox power sensor."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{name} Power"
        self._attr_unique_id = f"{device_id}_power"
        self._device = device

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("name", f"Device {self._device_id}"),
            "manufacturer": MANUFACTURER,
            "model": self._device.get("model", "Unknown"),
        }

    @property
    def native_value(self) -> float | None:
        """Return the power value."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("power")
        
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "W"
