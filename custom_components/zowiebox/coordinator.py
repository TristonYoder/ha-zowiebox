"""Data update coordinator for Zowiebox integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZowieboxAPI
from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ZowieboxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Zowiebox API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.api = ZowieboxAPI(
            host=entry.data["host"],
            port=entry.data.get("port", 80),
        )
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name="Zowiebox",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Get status and devices in parallel
            status_task = self.api.async_get_status()
            devices_task = self.api.async_get_devices()
            
            status, devices = await asyncio.gather(status_task, devices_task)
            
            return {
                "status": status,
                "devices": devices,
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def async_control_device(self, device_id: str, command: str, value: Any = None):
        """Control a device and refresh data."""
        try:
            result = await self.api.async_control_device(device_id, command, value)
            # Refresh data after control command
            await self.async_request_refresh()
            return result
        except Exception as err:
            _LOGGER.error("Error controlling device %s: %s", device_id, err)
            raise
