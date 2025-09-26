"""API client for ZowieTek devices."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from .const import (
    API_ENDPOINT_VIDEO,
    API_ENDPOINT_PTZ,
    API_ENDPOINT_AUDIO,
    API_ENDPOINT_STREAM,
    API_ENDPOINT_STREAMPLAY,
    API_ENDPOINT_NETWORK,
    API_ENDPOINT_SYSTEM,
    API_ENDPOINT_STORAGE,
    API_ENDPOINT_RECORD,
    LOGIN_CHECK_FLAG,
    OPTION_GET,
    OPTION_SET,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class ZowieboxAPI:
    """API client for ZowieTek devices."""

    def __init__(
        self,
        host: str,
        port: int = 80,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=DEFAULT_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        return f"http://{self._host}:{self._port}"

    async def async_get_status(self) -> dict[str, Any]:
        """Get device status using video endpoint."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {"group": "all"}
        
        _LOGGER.info("Making API request to: %s", url)
        _LOGGER.info("Request payload: %s", payload)
        
        try:
            async with session.post(url, json=payload) as response:
                _LOGGER.info("HTTP response status: %s", response.status)
                response.raise_for_status()
                data = await response.json()
                _LOGGER.info("API response: %s", data)
                return data
        except Exception as err:
            _LOGGER.error("Failed to get status from %s: %s", url, err)
            # Return a proper error response that the config flow can handle
            return {"status": "00003", "rsp": "error", "error": str(err)}

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Get list of devices - ZowieTek doesn't have a traditional device list."""
        # ZowieTek devices are single-purpose, so we return the device itself
        status = await self.async_get_status()
        if status.get("status") == "00000":
            return [{
                "id": "zowietek_device",
                "name": "ZowieTek Device",
                "type": "camera",
                "state": "on",
                "capabilities": ["ptz", "focus", "exposure", "white_balance", "image_control", "audio", "recording", "streaming"],
                "model": "ZowieTek",
                "status": "online"
            }]
        return []

    async def async_control_device(
        self, device_id: str, command: str, value: Any = None
    ) -> dict[str, Any]:
        """Control a device - generic control method."""
        _LOGGER.info("Control command: %s, value: %s", command, value)
        return {"status": "00000", "rsp": "succeed"}

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # ZowieTek-specific API methods based on documentation

    async def async_get_input_info(self) -> dict[str, Any]:
        """Get input signal information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "hdmi",
            "opt": "get_input_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_output_info(self) -> dict[str, Any]:
        """Get output information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "hdmi",
            "opt": "get_output_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_set_output_info(
        self,
        format: str | None = None,
        audio_switch: int | None = None,
        loop_out_switch: int | None = None
    ) -> dict[str, Any]:
        """Set output information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        data = {}
        if format is not None:
            data["format"] = format
        if audio_switch is not None:
            data["audio_switch"] = audio_switch
        if loop_out_switch is not None:
            data["loop_out_switch"] = loop_out_switch
        
        payload = {
            "group": "hdmi",
            "opt": "set_output_info",
            "data": data
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # PTZ Control
    async def async_get_ptz_info(self) -> dict[str, Any]:
        """Get PTZ configuration information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_PTZ}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "ptz",
            "opt": "get_ptz_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_set_ptz_info(
        self,
        protocol: int | None = None,
        type: int | None = None,
        ip: str | None = None,
        port: int | None = None,
        addr: int | None = None,
        addr_fix: int | None = None,
        baudrate_id: int | None = None
    ) -> dict[str, Any]:
        """Set PTZ configuration information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_PTZ}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        data = {}
        if protocol is not None:
            data["protocol"] = protocol
        if type is not None:
            data["type"] = type
        if ip is not None:
            data["ip"] = ip
        if port is not None:
            data["port"] = port
        if addr is not None:
            data["addr"] = addr
        if addr_fix is not None:
            data["addr_fix"] = addr_fix
        if baudrate_id is not None:
            data["baudrate_id"] = baudrate_id
        
        payload = {
            "group": "ptz",
            "opt": "set_ptz_info",
            "data": data
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # Encoding Control
    async def async_get_encoding_info(self) -> dict[str, Any]:
        """Get encoding parameters."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {"group": "all"}
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_set_encoding_info(self, venc_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Set encoding parameters."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_VIDEO}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "venc",
            "venc": venc_data
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # Audio Control
    async def async_get_audio_info(self) -> dict[str, Any]:
        """Get audio configuration information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_AUDIO}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {"group": "all"}
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_set_audio_info(self, audio_data: dict[str, Any]) -> dict[str, Any]:
        """Set audio configuration information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_AUDIO}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "audio",
            "audio": audio_data
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_audio_switch(self, switch: int) -> dict[str, Any]:
        """Turn audio on/off."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_AUDIO}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "audio_switch",
            "switch": switch
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # Streaming Control
    async def async_get_stream_info(self) -> dict[str, Any]:
        """Get stream information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_STREAM}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {"group": "getStreamStatus"}
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_add_stream_info(
        self,
        service: str,
        protocol: str,
        url: str,
        key: str,
        switch: int,
        desc: str,
        name: str
    ) -> dict[str, Any]:
        """Add stream information."""
        session = await self._get_session()
        url_endpoint = f"{self.base_url}{API_ENDPOINT_STREAM}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "publish",
            "opt": "add_publish_info",
            "data": {
                "service": service,
                "protocol": protocol,
                "url": url,
                "key": key,
                "switch": switch,
                "desc": desc,
                "name": name
            }
        }
        
        async with session.post(url_endpoint, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_start_stop_stream(self, index: int, switch: int) -> dict[str, Any]:
        """Start or stop streaming."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_STREAM}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "publish",
            "opt": "update_publish_switch",
            "data": {
                "index": index,
                "switch": switch
            }
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # Recording Control
    async def async_get_storage_status(self) -> dict[str, Any]:
        """Get storage device status."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_STORAGE}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {"group": "storage_status"}
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_recording_tasks(self) -> dict[str, Any]:
        """Get recording task list."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_RECORD}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "record",
            "opt": "get_task_list"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_start_stop_recording(self, index: str, enable: int) -> dict[str, Any]:
        """Start or stop recording."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_RECORD}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "record",
            "opt": "set_task_enable",
            "data": {
                "index": index,
                "enable": enable
            }
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # System Information
    async def async_get_system_time(self) -> dict[str, Any]:
        """Get device time."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_SYSTEM}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "systime",
            "opt": "get_systime_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_set_system_time(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        setting_mode_id: int,
        time_zone_id: str,
        ntp_enable: int = 0,
        ntp_server: str = "",
        ntp_port: int = 123
    ) -> dict[str, Any]:
        """Set device time."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_SYSTEM}?{OPTION_SET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "systime",
            "opt": "set_systime_info",
            "data": {
                "time": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second
                },
                "setting_mode_id": setting_mode_id,
                "time_zone_id": time_zone_id,
                "ntp_enable": ntp_enable,
                "ntp_server": ntp_server,
                "ntp_port": ntp_port
            }
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    # Network Information
    async def async_get_network_info(self) -> dict[str, Any]:
        """Get network information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_NETWORK}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "lan",
            "opt": "get_lan_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_wifi_info(self) -> dict[str, Any]:
        """Get WiFi connection information."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_NETWORK}?{OPTION_GET}&{LOGIN_CHECK_FLAG}"
        
        payload = {
            "group": "wifi",
            "opt": "get_wifi_info"
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()