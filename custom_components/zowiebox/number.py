"""
Number platform for Zowiebox integration.
"""

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ZowieboxDataUpdateCoordinator
from .decoder_controls import ZowieboxBitrateNumber, ZowieboxFramerateNumber
from .mode_aware_entities import (
    ZowieboxModeAwareBitrateNumber, 
    ZowieboxModeAwareFramerateNumber
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zowiebox number entities from a config entry."""
    coordinator: ZowieboxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Add mode-aware entities (these will show/hide based on device mode)
    entities.append(ZowieboxModeAwareBitrateNumber(coordinator))
    entities.append(ZowieboxModeAwareFramerateNumber(coordinator))

    # Add legacy entities for backward compatibility
    if coordinator.data and "streams" in coordinator.data:
        for stream_id, stream_data in coordinator.data["streams"].items():
            entities.append(ZowieboxBitrateNumber(coordinator, stream_id))
            entities.append(ZowieboxFramerateNumber(coordinator, stream_id))

    async_add_entities(entities)