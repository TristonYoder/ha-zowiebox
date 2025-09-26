"""Switch platform for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Zowiebox switch based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create switches for each device that supports switching
    switches = []
    if coordinator.data and "devices" in coordinator.data:
        for device in coordinator.data["devices"]:
            device_id = device.get("id")
            device_name = device.get("name", f"Device {device_id}")
            device_type = device.get("type", "unknown")
            
            # Create switches for devices that support on/off control
            if device_type in ["switch", "light", "outlet"]:
                switches.append(ZowieboxSwitch(coordinator, device_id, device_name, device))

    async_add_entities(switches)


class ZowieboxSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Zowiebox switch."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_switch"
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
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("state") == "on"
        
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.async_control_device(self._device_id, "turn_on")
        except Exception as err:
            _LOGGER.error("Error turning on device %s: %s", self._device_id, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.async_control_device(self._device_id, "turn_off")
        except Exception as err:
            _LOGGER.error("Error turning off device %s: %s", self._device_id, err)
            raise
