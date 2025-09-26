"""
Decoder configuration controls for ZowieTek devices.
Handles resolution, codec, bitrate, and other decoder settings.
"""

import logging
from typing import Any
from homeassistant.components.select import SelectEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER
from .coordinator import ZowieboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ZowieboxResolutionSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing video resolution."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str) -> None:
        """Initialize the resolution select entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._attr_name = f"Stream {stream_id} Resolution"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_resolution_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if not self.coordinator.data:
            return None
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        width = stream_data.get("width", 0)
        height = stream_data.get("height", 0)
        
        if width and height:
            return f"{width}x{height}"
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available resolution options."""
        if not self.coordinator.data:
            return []
        
        # Get available resolutions from device
        device_info = self.coordinator.data.get("device_info", {})
        resolution_list = device_info.get("resolution_list", [])
        
        options = []
        for resolution in resolution_list:
            width = resolution.get("width", 0)
            height = resolution.get("height", 0)
            if width and height:
                options.append(f"{width}x{height}")
        
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected resolution."""
        if not self.coordinator.data:
            return
        
        try:
            # Parse resolution
            width, height = option.split("x")
            width = int(width)
            height = int(height)
            
            # Update stream resolution
            await self.coordinator.api.async_set_output_info(
                self._stream_id, "set_resolution",
                {"width": width, "height": height}
            )
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set resolution %s: %s", option, err)


class ZowieboxCodecSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing video codec."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str) -> None:
        """Initialize the codec select entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._attr_name = f"Stream {stream_id} Codec"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_codec_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if not self.coordinator.data:
            return None
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        codec_info = stream_data.get("codec", {})
        selected_id = codec_info.get("selected_id", 0)
        codec_list = codec_info.get("codec_list", [])
        
        if selected_id < len(codec_list):
            return codec_list[selected_id]
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available codec options."""
        if not self.coordinator.data:
            return []
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        codec_info = stream_data.get("codec", {})
        return codec_info.get("codec_list", [])

    async def async_select_option(self, option: str) -> None:
        """Change the selected codec."""
        if not self.coordinator.data:
            return
        
        try:
            # Find codec index
            codec_list = self.options
            if option in codec_list:
                codec_index = codec_list.index(option)
                
                # Update stream codec
                await self.coordinator.api.async_set_output_info(
                    self._stream_id, "set_codec",
                    {"codec_id": codec_index}
                )
                
                # Refresh coordinator data
                await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set codec %s: %s", option, err)


class ZowieboxBitrateNumber(CoordinatorEntity, NumberEntity):
    """Number entity for setting video bitrate."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str) -> None:
        """Initialize the bitrate number entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._attr_name = f"Stream {stream_id} Bitrate"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_bitrate_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )
        
        # Set bitrate limits (in bps)
        self._attr_native_min_value = 100000  # 100 kbps
        self._attr_native_max_value = 50000000  # 50 Mbps
        self._attr_native_step = 100000  # 100 kbps steps
        self._attr_native_unit_of_measurement = "bps"

    @property
    def native_value(self) -> float | None:
        """Return the current bitrate value."""
        if not self.coordinator.data:
            return None
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        return stream_data.get("bitrate", 0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the bitrate value."""
        if not self.coordinator.data:
            return
        
        try:
            # Update stream bitrate
            await self.coordinator.api.async_set_output_info(
                self._stream_id, "set_bitrate",
                {"bitrate": int(value)}
            )
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set bitrate %s: %s", value, err)


class ZowieboxFramerateNumber(CoordinatorEntity, NumberEntity):
    """Number entity for setting video framerate."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str) -> None:
        """Initialize the framerate number entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._attr_name = f"Stream {stream_id} Framerate"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_framerate_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )
        
        # Set framerate limits
        self._attr_native_min_value = 1.0
        self._attr_native_max_value = 60.0
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "fps"

    @property
    def native_value(self) -> float | None:
        """Return the current framerate value."""
        if not self.coordinator.data:
            return None
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        return stream_data.get("framerate", 0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the framerate value."""
        if not self.coordinator.data:
            return
        
        try:
            # Update stream framerate
            await self.coordinator.api.async_set_output_info(
                self._stream_id, "set_framerate",
                {"framerate": value}
            )
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set framerate %s: %s", value, err)


class ZowieboxStreamSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for enabling/disabling streams."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str, stream_name: str) -> None:
        """Initialize the stream switch entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._stream_name = stream_name
        self._attr_name = f"Stream {stream_name}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_switch_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )

    @property
    def is_on(self) -> bool:
        """Return true if the stream is active."""
        if not self.coordinator.data:
            return False
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        return stream_data.get("switch") == 1

    async def async_turn_on(self) -> None:
        """Turn on the stream."""
        await self._set_stream_state(True)

    async def async_turn_off(self) -> None:
        """Turn off the stream."""
        await self._set_stream_state(False)

    async def _set_stream_state(self, state: bool) -> None:
        """Set the stream state."""
        if not self.coordinator.data:
            return
        
        try:
            switch_value = 1 if state else 0
            
            # Update stream switch
            await self.coordinator.api.async_set_output_info(
                self._stream_id, "set_output_switch",
                {"switch": switch_value}
            )
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set stream state %s: %s", state, err)
