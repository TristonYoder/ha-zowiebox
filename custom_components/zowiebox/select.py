"""
Select platform for Zowiebox integration.
"""

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZowieboxDataUpdateCoordinator
from .stream_manager import ZowieboxStreamSelect
from .decoder_controls import ZowieboxResolutionSelect, ZowieboxCodecSelect

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zowiebox select entities from a config entry."""
    coordinator: ZowieboxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Add stream selection entity
    entities.append(ZowieboxStreamSelect(coordinator))

    # Add resolution and codec selectors for each stream
    if coordinator.data and "streams" in coordinator.data:
        for stream_id, stream_data in coordinator.data["streams"].items():
            entities.append(ZowieboxResolutionSelect(coordinator, stream_id))
            entities.append(ZowieboxCodecSelect(coordinator, stream_id))

    async_add_entities(entities)