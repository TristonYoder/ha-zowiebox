"""Light platform for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ColorMode,
    LightEntity,
)
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
    """Set up Zowiebox light based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create lights for each device that supports lighting
    lights = []
    if coordinator.data and "devices" in coordinator.data:
        for device in coordinator.data["devices"]:
            device_id = device.get("id")
            device_name = device.get("name", f"Device {device_id}")
            device_type = device.get("type", "unknown")
            
            # Create lights for devices that support lighting
            if device_type == "light":
                lights.append(ZowieboxLight(coordinator, device_id, device_name, device))

    async_add_entities(lights)


class ZowieboxLight(CoordinatorEntity, LightEntity):
    """Representation of a Zowiebox light."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_light"
        self._device = device
        
        # Set supported color modes based on device capabilities
        capabilities = device.get("capabilities", [])
        supported_modes = {ColorMode.ONOFF}
        
        if "brightness" in capabilities:
            supported_modes.add(ColorMode.BRIGHTNESS)
        if "color_temp" in capabilities:
            supported_modes.add(ColorMode.COLOR_TEMP)
        if "color" in capabilities:
            supported_modes.add(ColorMode.RGB)
            
        self._attr_supported_color_modes = supported_modes

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
        """Return true if the light is on."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("state") == "on"
        
        return None

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                brightness = device.get("brightness")
                if brightness is not None:
                    return int(brightness * 255 / 100)  # Convert percentage to 0-255
        return None

    @property
    def color_temp(self) -> int | None:
        """Return the color temperature of the light."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("color_temp")
        return None

    @property
    def min_mireds(self) -> int:
        """Return the coldest color_temp that this light supports."""
        return 153  # 6500K

    @property
    def max_mireds(self) -> int:
        """Return the warmest color_temp that this light supports."""
        return 500  # 2000K

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        try:
            # Prepare control command
            command_data = {"command": "turn_on"}
            
            # Add brightness if specified
            if ATTR_BRIGHTNESS in kwargs:
                brightness = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)  # Convert 0-255 to percentage
                command_data["brightness"] = brightness
            
            # Add color temperature if specified
            if ATTR_COLOR_TEMP in kwargs:
                command_data["color_temp"] = kwargs[ATTR_COLOR_TEMP]
            
            await self.coordinator.async_control_device(self._device_id, "turn_on", command_data)
        except Exception as err:
            _LOGGER.error("Error turning on light %s: %s", self._device_id, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self.coordinator.async_control_device(self._device_id, "turn_off")
        except Exception as err:
            _LOGGER.error("Error turning off light %s: %s", self._device_id, err)
            raise
