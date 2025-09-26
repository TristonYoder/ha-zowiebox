"""API client for Zowiebox devices."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from .const import (
    API_ENDPOINT_CONTROL,
    API_ENDPOINT_DEVICES,
    API_ENDPOINT_STATUS,
    API_ENDPOINT_CAMERA_INFO,
    API_ENDPOINT_PTZ_CONTROL,
    API_ENDPOINT_FOCUS_CONTROL,
    API_ENDPOINT_ZOOM_CONTROL,
    API_ENDPOINT_EXPOSURE_CONTROL,
    API_ENDPOINT_WHITE_BALANCE,
    API_ENDPOINT_IMAGE_CONTROL,
    API_ENDPOINT_AUDIO_CONTROL,
    API_ENDPOINT_STREAM_CONTROL,
    API_ENDPOINT_RECORDING_CONTROL,
    API_ENDPOINT_TALLY_CONTROL,
    API_ENDPOINT_NDI_CONTROL,
    API_ENDPOINT_DEVICE_CONTROL,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class ZowieboxAPI:
    """API client for Zowiebox devices."""

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
        """Get device status."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_STATUS}"
        
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Get list of devices."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_DEVICES}"
        
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def async_control_device(
        self, device_id: str, command: str, value: Any = None
    ) -> dict[str, Any]:
        """Control a device."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_CONTROL}"
        
        payload = {
            "device_id": device_id,
            "command": command,
        }
        if value is not None:
            payload["value"] = value
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # Zowietek-specific camera control methods
    
    async def async_get_camera_info(self) -> dict[str, Any]:
        """Get camera information and capabilities."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_CAMERA_INFO}"
        
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def async_ptz_control(
        self, 
        pan: int | None = None, 
        tilt: int | None = None, 
        zoom: int | None = None,
        speed: int = 5
    ) -> dict[str, Any]:
        """Control PTZ camera movement."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_PTZ_CONTROL}"
        
        payload = {
            "pan": pan,
            "tilt": tilt,
            "zoom": zoom,
            "speed": speed
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_focus_control(
        self,
        focus_mode: str | None = None,
        focus_speed: int | None = None,
        focus_area: str | None = None,
        x_percent: float | None = None,
        y_percent: float | None = None,
        af_sensitivity: str | None = None,
        af_lock: bool | None = None
    ) -> dict[str, Any]:
        """Control camera focus settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_FOCUS_CONTROL}"
        
        payload = {
            "focus_mode": focus_mode,
            "focus_speed": focus_speed,
            "focus_area": focus_area,
            "x_percent": x_percent,
            "y_percent": y_percent,
            "af_sensitivity": af_sensitivity,
            "af_lock": af_lock
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_zoom_control(
        self,
        digital_zoom: int | None = None,
        digital_zoom_enable: bool | None = None,
        zoom_speed: int | None = None
    ) -> dict[str, Any]:
        """Control camera zoom settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_ZOOM_CONTROL}"
        
        payload = {
            "digital_zoom": digital_zoom,
            "digital_zoom_enable": digital_zoom_enable,
            "zoom_speed": zoom_speed
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_exposure_control(
        self,
        mode: str | None = None,
        gain: int | None = None,
        shutter: int | None = None,
        wdr: bool | None = None,
        flicker: str | None = None,
        bias: int | None = None,
        backlight: bool | None = None,
        metering: str | None = None,
        sensitive: int | None = None,
        ae_lock: bool | None = None
    ) -> dict[str, Any]:
        """Control camera exposure settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_EXPOSURE_CONTROL}"
        
        payload = {
            "mode": mode,
            "gain": gain,
            "shutter": shutter,
            "wdr": wdr,
            "flicker": flicker,
            "bias": bias,
            "backlight": backlight,
            "metering": metering,
            "sensitive": sensitive,
            "ae_lock": ae_lock
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_white_balance_control(
        self,
        mode: str | None = None,
        var: int | None = None,
        rgain: int | None = None,
        bgain: int | None = None,
        saturation: int | None = None,
        hue: int | None = None,
        ircut: bool | None = None
    ) -> dict[str, Any]:
        """Control camera white balance settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_WHITE_BALANCE}"
        
        payload = {
            "mode": mode,
            "var": var,
            "rgain": rgain,
            "bgain": bgain,
            "saturation": saturation,
            "hue": hue,
            "ircut": ircut
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_image_control(
        self,
        brightness: int | None = None,
        contrast: int | None = None,
        sharpness: int | None = None,
        gamma: int | None = None,
        flip: bool | None = None,
        color_gray: str | None = None,
        noise_reduction_2d: int | None = None,
        noise_reduction_3d: int | None = None,
        correction: int | None = None,
        image_style: str | None = None
    ) -> dict[str, Any]:
        """Control camera image settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_IMAGE_CONTROL}"
        
        payload = {
            "brightness": brightness,
            "contrast": contrast,
            "sharpness": sharpness,
            "gamma": gamma,
            "flip": flip,
            "color_gray": color_gray,
            "noise_reduction_2d": noise_reduction_2d,
            "noise_reduction_3d": noise_reduction_3d,
            "correction": correction,
            "image_style": image_style
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_audio_control(
        self,
        ai_type: str | None = None,
        switch: bool | None = None,
        codec: str | None = None,
        bitrate: int | None = None,
        sample_rate: int | None = None,
        channel: int | None = None,
        volume: int | None = None,
        ao_devtype: str | None = None
    ) -> dict[str, Any]:
        """Control camera audio settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_AUDIO_CONTROL}"
        
        payload = {
            "ai_type": ai_type,
            "switch": switch,
            "codec": codec,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "channel": channel,
            "volume": volume,
            "ao_devtype": ao_devtype
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_stream_control(
        self,
        name: str | None = None,
        url: str | None = None,
        streamtype: str | None = None,
        switch: bool | None = None,
        index: int | None = None
    ) -> dict[str, Any]:
        """Control streaming settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_STREAM_CONTROL}"
        
        payload = {
            "name": name,
            "url": url,
            "streamtype": streamtype,
            "switch": switch,
            "index": index
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_recording_control(
        self,
        index: int | None = None,
        command: str | None = None
    ) -> dict[str, Any]:
        """Control recording functionality."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_RECORDING_CONTROL}"
        
        payload = {
            "index": index,
            "command": command
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_tally_control(
        self,
        color_id: str | None = None,
        mode_id: str | None = None,
        switch: str | None = None
    ) -> dict[str, Any]:
        """Control tally light settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_TALLY_CONTROL}"
        
        payload = {
            "color_id": color_id,
            "mode_id": mode_id,
            "switch": switch
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_ndi_control(
        self,
        ndi_name: str | None = None,
        groups: str | None = None,
        switch_value: bool | None = None
    ) -> dict[str, Any]:
        """Control NDI settings."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_NDI_CONTROL}"
        
        payload = {
            "ndi_name": ndi_name,
            "groups": groups,
            "switch_value": switch_value
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def async_device_control(
        self,
        device_time: str | None = None,
        setting_mode_id: str | None = None,
        time_zone_id: str | None = None,
        ntp_enable: bool | None = None,
        ntp_server: str | None = None,
        ntp_port: int | None = None,
        reboot: bool | None = None
    ) -> dict[str, Any]:
        """Control device settings and time."""
        session = await self._get_session()
        url = f"{self.base_url}{API_ENDPOINT_DEVICE_CONTROL}"
        
        payload = {
            "device_time": device_time,
            "setting_mode_id": setting_mode_id,
            "time_zone_id": time_zone_id,
            "ntp_enable": ntp_enable,
            "ntp_server": ntp_server,
            "ntp_port": ntp_port,
            "reboot": reboot
        }
        
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()