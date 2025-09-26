"""Number platform for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
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
    """Set up Zowiebox number entities based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Import camera control entities
    from .camera_control import async_setup_entry as async_setup_camera_control
    
    # Set up camera control entities (which include number entities)
    await async_setup_camera_control(hass, entry, async_add_entities)
