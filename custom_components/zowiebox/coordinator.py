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
            
            # Get additional stream and audio information
            stream_info = await self.api.async_get_stream_info()
            audio_info = await self.api.async_get_audio_config_info()
            
            # Parse stream data
            streams = {}
            rtsp_streams = []
            srt_streams = []
            
            if status.get("status") == "00000":
                video_data = status.get("all", {})
                
                # Parse video streams
                venc_list = video_data.get("venc", [])
                for i, venc in enumerate(venc_list):
                    stream_id = venc.get("stream_id", i)
                    streams[str(stream_id)] = {
                        "stream_id": stream_id,
                        "name": f"Stream {stream_id}",
                        "type": "main" if stream_id == 0 else "sub",
                        "switch": 1,  # Default to active
                        "width": venc.get("width", 0),
                        "height": venc.get("height", 0),
                        "framerate": venc.get("framerate", 0),
                        "bitrate": venc.get("bitrate", 0),
                        "codec": venc.get("codec", {}),
                        "profile": venc.get("profile", {}),
                        "ratecontrol": venc.get("ratecontrol", {}),
                    }
            
            if stream_info.get("status") == "00000":
                stream_data = stream_info.get("all", {})
                
                # Parse RTSP streams
                rtsp_list = stream_data.get("rtsp", [])
                for rtsp in rtsp_list:
                    rtsp_streams.append({
                        "stream_id": rtsp.get("stream_id", 0),
                        "name": rtsp.get("name", "RTSP Stream"),
                        "switch": rtsp.get("switch", 0),
                        "url": rtsp.get("url", ""),
                        "width": rtsp.get("width", 0),
                        "height": rtsp.get("height", 0),
                        "framerate": rtsp.get("framerate", 0),
                        "venctype": rtsp.get("venctype", 0),
                        "aenctype": rtsp.get("aenctype", 0),
                    })
                
                # Parse SRT streams
                srt_list = stream_data.get("srt_servers", [])
                for srt in srt_list:
                    srt_streams.append({
                        "stream_id": srt.get("stream_id", 0),
                        "name": srt.get("name", "SRT Stream"),
                        "switch": srt.get("switch", 0),
                        "url": srt.get("url", ""),
                        "port": srt.get("port", 0),
                        "streamId": srt.get("streamId", ""),
                    })
            
            return {
                "status": status,
                "devices": devices,
                "streams": streams,
                "rtsp_streams": rtsp_streams,
                "srt_streams": srt_streams,
                "audio_info": audio_info,
                "device_info": status.get("all", {}) if status.get("status") == "00000" else {},
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
