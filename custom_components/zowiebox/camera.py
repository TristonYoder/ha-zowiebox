"""Camera platform for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.camera import Camera
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
    """Set up Zowiebox camera based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create cameras for each device that supports video streaming
    cameras = []
    if coordinator.data and "devices" in coordinator.data:
        for device in coordinator.data["devices"]:
            device_id = device.get("id")
            device_name = device.get("name", f"Device {device_id}")
            device_type = device.get("type", "unknown")
            
            # Create cameras for devices that support video streaming
            if device_type in ["camera", "ptz"] and "streaming" in device.get("capabilities", []):
                cameras.append(ZowieboxCamera(coordinator, device_id, device_name, device))

    async_add_entities(cameras)


class ZowieboxCamera(CoordinatorEntity, Camera):
    """Representation of a Zowiebox camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_camera"
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
    def is_recording(self) -> bool:
        """Return true if the camera is recording."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return False
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("recording", False)
        
        return False

    @property
    def is_streaming(self) -> bool:
        """Return true if the camera is streaming."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return False
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("streaming", False)
        
        return False

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        try:
            # Get the stream URL from device data
            if not self.coordinator.data or "devices" not in self.coordinator.data:
                return None
            
            for device in self.coordinator.data["devices"]:
                if device.get("id") == self._device_id:
                    stream_url = device.get("stream_url")
                    if stream_url:
                        # Use the coordinator's API to get the image
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(stream_url) as response:
                                if response.status == 200:
                                    return await response.read()
        except Exception as err:
            _LOGGER.error("Error getting camera image for %s: %s", self._device_id, err)
        
        return None

    async def async_turn_on(self) -> None:
        """Turn on the camera."""
        try:
            await self.coordinator.async_control_device(self._device_id, "turn_on")
        except Exception as err:
            _LOGGER.error("Error turning on camera %s: %s", self._device_id, err)
            raise

    async def async_turn_off(self) -> None:
        """Turn off the camera."""
        try:
            await self.coordinator.async_control_device(self._device_id, "turn_off")
        except Exception as err:
            _LOGGER.error("Error turning off camera %s: %s", self._device_id, err)
            raise
