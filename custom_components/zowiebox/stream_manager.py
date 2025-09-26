"""
Stream management for ZowieTek devices.
Handles stream discovery, configuration, and control.
"""

import logging
from typing import Any
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.camera import Camera
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER
from .coordinator import ZowieboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ZowieboxStreamSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing active stream."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator) -> None:
        """Initialize the stream select entity."""
        super().__init__(coordinator)
        self._attr_name = "Active Stream"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_active_stream"
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
        
        # Find the currently active stream
        streams = self.coordinator.data.get("streams", {})
        for stream_id, stream_data in streams.items():
            if stream_data.get("switch") == 1:
                return stream_data.get("name", f"Stream {stream_id}")
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        if not self.coordinator.data:
            return []
        
        options = []
        streams = self.coordinator.data.get("streams", {})
        
        # Add main streams
        for stream_id, stream_data in streams.items():
            if stream_data.get("type") == "main":
                name = stream_data.get("name", f"Main Stream {stream_id}")
                options.append(name)
        
        # Add sub streams
        for stream_id, stream_data in streams.items():
            if stream_data.get("type") == "sub":
                name = stream_data.get("name", f"Sub Stream {stream_id}")
                options.append(name)
        
        # Add RTSP streams
        rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
        for stream in rtsp_streams:
            if stream.get("switch") == 1:
                name = stream.get("name", f"RTSP {stream.get('stream_id', 'unknown')}")
                options.append(name)
        
        # Add SRT streams
        srt_streams = self.coordinator.data.get("srt_streams", [])
        for stream in srt_streams:
            if stream.get("switch") == 1:
                name = stream.get("name", f"SRT {stream.get('stream_id', 'unknown')}")
                options.append(name)
        
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if not self.coordinator.data:
            return
        
        # Find the stream to activate
        target_stream = None
        streams = self.coordinator.data.get("streams", {})
        
        # Check main streams
        for stream_id, stream_data in streams.items():
            if stream_data.get("name") == option:
                target_stream = stream_id
                break
        
        # Check RTSP streams
        if not target_stream:
            rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
            for stream in rtsp_streams:
                if stream.get("name") == option:
                    target_stream = stream.get("stream_id")
                    break
        
        # Check SRT streams
        if not target_stream:
            srt_streams = self.coordinator.data.get("srt_streams", [])
            for stream in srt_streams:
                if stream.get("name") == option:
                    target_stream = stream.get("stream_id")
                    break
        
        if target_stream is not None:
            # Deactivate all streams first
            await self._deactivate_all_streams()
            
            # Activate the selected stream
            await self._activate_stream(target_stream)
            
            # Refresh coordinator data
            await self.coordinator.async_request_refresh()

    async def _deactivate_all_streams(self) -> None:
        """Deactivate all streams."""
        try:
            # Deactivate main streams
            await self.coordinator.api.async_set_output_info("main", "set_output_switch", {"switch": 0})
            await self.coordinator.api.async_set_output_info("sub", "set_output_switch", {"switch": 0})
            
            # Deactivate RTSP streams
            rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
            for stream in rtsp_streams:
                if stream.get("switch") == 1:
                    await self.coordinator.api.async_publish_stream_info(
                        "rtsp", "set_rtsp_switch", 
                        {"stream_id": stream.get("stream_id"), "switch": 0}
                    )
            
            # Deactivate SRT streams
            srt_streams = self.coordinator.data.get("srt_streams", [])
            for stream in srt_streams:
                if stream.get("switch") == 1:
                    await self.coordinator.api.async_publish_stream_info(
                        "srt", "set_srt_switch",
                        {"stream_id": stream.get("stream_id"), "switch": 0}
                    )
        except Exception as err:
            _LOGGER.error("Failed to deactivate streams: %s", err)

    async def _activate_stream(self, stream_id: int) -> None:
        """Activate a specific stream."""
        try:
            if stream_id == 0:  # Main stream
                await self.coordinator.api.async_set_output_info("main", "set_output_switch", {"switch": 1})
            elif stream_id == 1:  # Sub stream
                await self.coordinator.api.async_set_output_info("sub", "set_output_switch", {"switch": 1})
            else:
                # Handle RTSP/SRT streams
                rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
                for stream in rtsp_streams:
                    if stream.get("stream_id") == stream_id:
                        await self.coordinator.api.async_publish_stream_info(
                            "rtsp", "set_rtsp_switch",
                            {"stream_id": stream_id, "switch": 1}
                        )
                        break
                
                srt_streams = self.coordinator.data.get("srt_streams", [])
                for stream in srt_streams:
                    if stream.get("stream_id") == stream_id:
                        await self.coordinator.api.async_publish_stream_info(
                            "srt", "set_srt_switch",
                            {"stream_id": stream_id, "switch": 1}
                        )
                        break
        except Exception as err:
            _LOGGER.error("Failed to activate stream %s: %s", stream_id, err)


class ZowieboxStreamSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for stream information."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str, stream_name: str) -> None:
        """Initialize the stream sensor entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._stream_name = stream_name
        self._attr_name = f"Stream {stream_name} Status"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_stream_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "Unknown"
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        if stream_data.get("switch") == 1:
            return "Active"
        else:
            return "Inactive"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        return {
            "stream_id": self._stream_id,
            "stream_name": self._stream_name,
            "resolution": stream_data.get("resolution", "Unknown"),
            "codec": stream_data.get("codec", "Unknown"),
            "bitrate": stream_data.get("bitrate", 0),
            "framerate": stream_data.get("framerate", 0),
            "url": stream_data.get("url", ""),
        }


class ZowieboxStreamCamera(CoordinatorEntity, Camera):
    """Camera entity for stream viewing."""

    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, stream_id: str, stream_name: str) -> None:
        """Initialize the stream camera entity."""
        super().__init__(coordinator)
        self._stream_id = stream_id
        self._stream_name = stream_name
        self._attr_name = f"Stream {stream_name}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_camera_{stream_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )

    @property
    def is_recording(self) -> bool:
        """Return true if the device is recording."""
        if not self.coordinator.data:
            return False
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        return stream_data.get("switch") == 1

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return a snapshot from the camera."""
        if not self.coordinator.data:
            return None
        
        streams = self.coordinator.data.get("streams", {})
        stream_data = streams.get(self._stream_id, {})
        
        if stream_data.get("switch") != 1:
            return None
        
        # Get snapshot from the stream
        try:
            snapshot_url = stream_data.get("snapshot_url")
            if snapshot_url:
                # Use the snapshot URL if available
                return await self._get_snapshot_from_url(snapshot_url)
            else:
                # Use the main stream URL for snapshot
                stream_url = stream_data.get("url")
                if stream_url:
                    return await self._get_snapshot_from_url(stream_url)
        except Exception as err:
            _LOGGER.error("Failed to get camera image: %s", err)
        
        return None

    async def _get_snapshot_from_url(self, url: str) -> bytes | None:
        """Get snapshot from URL."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as err:
            _LOGGER.error("Failed to get snapshot from %s: %s", url, err)
        return None
