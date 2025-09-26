"""Config flow for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)

    # Create the API client to test connection
    from .api import ZowieboxAPI

    api = ZowieboxAPI(host, port)
    
    try:
        # Test the ZowieTek API using the correct endpoint structure
        _LOGGER.info("Testing connection to ZowieTek device at %s:%s", host, port)
        status = await api.async_get_status()
        
        _LOGGER.info("API response status: %s", status.get("status"))
        _LOGGER.info("API response rsp: %s", status.get("rsp"))
        
        if status.get("status") == "00000":
            _LOGGER.info("Successfully connected to ZowieTek device at %s:%s", host, port)
            _LOGGER.debug("Device status: %s", status)
        else:
            error_msg = status.get("rsp", "Unknown error")
            _LOGGER.error("ZowieTek API error: %s", error_msg)
            _LOGGER.error("Full response: %s", status)
            raise CannotConnect(f"API error: {error_msg}")
        
    except aiohttp.ClientError as err:
        _LOGGER.error("Network error connecting to %s:%s: %s", host, port, err)
        raise CannotConnect(f"Network error: {err}")
    except Exception as err:
        _LOGGER.error("Error connecting to %s:%s: %s", host, port, err)
        raise CannotConnect(f"Connection failed: {err}")

    # Return info that you want to store in the config entry.
    return {"title": f"Zowietek {host}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zowiebox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
