"""
Camera platform for Zowiebox integration.
"""

import logging
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZowieboxDataUpdateCoordinator
from .stream_manager import ZowieboxStreamCamera

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zowiebox camera entities from a config entry."""
    coordinator: ZowieboxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Add camera entities for each stream
    if coordinator.data and "streams" in coordinator.data:
        for stream_id, stream_data in coordinator.data["streams"].items():
            stream_name = stream_data.get("name", f"Stream {stream_id}")
            entities.append(ZowieboxStreamCamera(coordinator, stream_id, stream_name))

    async_add_entities(entities)