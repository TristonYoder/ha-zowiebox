"""Camera control entities for Zowiebox integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
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
    """Set up Zowiebox camera control entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    if coordinator.data and "devices" in coordinator.data:
        for device in coordinator.data["devices"]:
            device_id = device.get("id")
            device_name = device.get("name", f"Device {device_id}")
            device_type = device.get("type", "unknown")
            capabilities = device.get("capabilities", [])
            
            # Create camera control entities based on capabilities
            if device_type in ["camera", "ptz"]:
                if "ptz" in capabilities:
                    entities.extend([
                        ZowieboxPanControl(coordinator, device_id, device_name, device),
                        ZowieboxTiltControl(coordinator, device_id, device_name, device),
                        ZowieboxZoomControl(coordinator, device_id, device_name, device),
                    ])
                
                if "focus" in capabilities:
                    entities.extend([
                        ZowieboxFocusControl(coordinator, device_id, device_name, device),
                        ZowieboxFocusSpeedControl(coordinator, device_id, device_name, device),
                    ])
                
                if "exposure" in capabilities:
                    entities.extend([
                        ZowieboxGainControl(coordinator, device_id, device_name, device),
                        ZowieboxShutterControl(coordinator, device_id, device_name, device),
                        ZowieboxExposureModeSelect(coordinator, device_id, device_name, device),
                    ])
                
                if "white_balance" in capabilities:
                    entities.extend([
                        ZowieboxWhiteBalanceModeSelect(coordinator, device_id, device_name, device),
                        ZowieboxSaturationControl(coordinator, device_id, device_name, device),
                    ])
                
                if "image_control" in capabilities:
                    entities.extend([
                        ZowieboxBrightnessControl(coordinator, device_id, device_name, device),
                        ZowieboxContrastControl(coordinator, device_id, device_name, device),
                        ZowieboxSharpnessControl(coordinator, device_id, device_name, device),
                    ])
                
                if "audio" in capabilities:
                    entities.extend([
                        ZowieboxAudioVolumeControl(coordinator, device_id, device_name, device),
                        ZowieboxAudioSwitch(coordinator, device_id, device_name, device),
                    ])
                
                if "recording" in capabilities:
                    entities.append(ZowieboxRecordingSwitch(coordinator, device_id, device_name, device))
                
                if "tally" in capabilities:
                    entities.extend([
                        ZowieboxTallyColorSelect(coordinator, device_id, device_name, device),
                        ZowieboxTallyModeSelect(coordinator, device_id, device_name, device),
                    ])

    async_add_entities(entities)


class ZowieboxCameraControlEntity(CoordinatorEntity):
    """Base class for Zowiebox camera control entities."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        """Initialize the camera control entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device = device

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device.get("name", f"Device {self._device_id}"),
            "manufacturer": MANUFACTURER,
            "model": self._device.get("model", "Unknown"),
        }


# PTZ Controls
class ZowieboxPanControl(ZowieboxCameraControlEntity, NumberEntity):
    """Pan control for PTZ camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Pan"
        self._attr_unique_id = f"{device_id}_pan"
        self._attr_native_min_value = -180
        self._attr_native_max_value = 180
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current pan position."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("pan_position", 0)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set pan position."""
        try:
            await self.coordinator.api.async_ptz_control(pan=int(value))
        except Exception as err:
            _LOGGER.error("Error setting pan for %s: %s", self._device_id, err)
            raise


class ZowieboxTiltControl(ZowieboxCameraControlEntity, NumberEntity):
    """Tilt control for PTZ camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Tilt"
        self._attr_unique_id = f"{device_id}_tilt"
        self._attr_native_min_value = -90
        self._attr_native_max_value = 90
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current tilt position."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("tilt_position", 0)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set tilt position."""
        try:
            await self.coordinator.api.async_ptz_control(tilt=int(value))
        except Exception as err:
            _LOGGER.error("Error setting tilt for %s: %s", self._device_id, err)
            raise


class ZowieboxZoomControl(ZowieboxCameraControlEntity, NumberEntity):
    """Zoom control for PTZ camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Zoom"
        self._attr_unique_id = f"{device_id}_zoom"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 20
        self._attr_native_step = 0.1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current zoom level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("zoom_level", 1)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set zoom level."""
        try:
            await self.coordinator.api.async_ptz_control(zoom=int(value * 10))
        except Exception as err:
            _LOGGER.error("Error setting zoom for %s: %s", self._device_id, err)
            raise


# Focus Controls
class ZowieboxFocusControl(ZowieboxCameraControlEntity, NumberEntity):
    """Focus control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Focus"
        self._attr_unique_id = f"{device_id}_focus"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current focus level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("focus_level", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set focus level."""
        try:
            await self.coordinator.api.async_focus_control(focus_speed=int(value))
        except Exception as err:
            _LOGGER.error("Error setting focus for %s: %s", self._device_id, err)
            raise


class ZowieboxFocusSpeedControl(ZowieboxCameraControlEntity, NumberEntity):
    """Focus speed control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Focus Speed"
        self._attr_unique_id = f"{device_id}_focus_speed"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 10
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current focus speed."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("focus_speed", 5)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set focus speed."""
        try:
            await self.coordinator.api.async_focus_control(focus_speed=int(value))
        except Exception as err:
            _LOGGER.error("Error setting focus speed for %s: %s", self._device_id, err)
            raise


# Exposure Controls
class ZowieboxGainControl(ZowieboxCameraControlEntity, NumberEntity):
    """Gain control for camera exposure."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Gain"
        self._attr_unique_id = f"{device_id}_gain"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current gain level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("gain", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set gain level."""
        try:
            await self.coordinator.api.async_exposure_control(gain=int(value))
        except Exception as err:
            _LOGGER.error("Error setting gain for %s: %s", self._device_id, err)
            raise


class ZowieboxShutterControl(ZowieboxCameraControlEntity, NumberEntity):
    """Shutter speed control for camera exposure."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Shutter"
        self._attr_unique_id = f"{device_id}_shutter"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 10000
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self) -> float | None:
        """Return current shutter speed."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("shutter_speed", 100)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set shutter speed."""
        try:
            await self.coordinator.api.async_exposure_control(shutter=int(value))
        except Exception as err:
            _LOGGER.error("Error setting shutter for %s: %s", self._device_id, err)
            raise


class ZowieboxExposureModeSelect(ZowieboxCameraControlEntity, SelectEntity):
    """Exposure mode selection."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Exposure Mode"
        self._attr_unique_id = f"{device_id}_exposure_mode"
        self._attr_options = ["auto", "manual", "shutter_priority", "aperture_priority"]

    @property
    def current_option(self) -> str | None:
        """Return current exposure mode."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("exposure_mode", "auto")
        return None

    async def async_select_option(self, option: str) -> None:
        """Set exposure mode."""
        try:
            await self.coordinator.api.async_exposure_control(mode=option)
        except Exception as err:
            _LOGGER.error("Error setting exposure mode for %s: %s", self._device_id, err)
            raise


# White Balance Controls
class ZowieboxWhiteBalanceModeSelect(ZowieboxCameraControlEntity, SelectEntity):
    """White balance mode selection."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} White Balance Mode"
        self._attr_unique_id = f"{device_id}_wb_mode"
        self._attr_options = ["auto", "manual", "daylight", "tungsten", "fluorescent"]

    @property
    def current_option(self) -> str | None:
        """Return current white balance mode."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("white_balance_mode", "auto")
        return None

    async def async_select_option(self, option: str) -> None:
        """Set white balance mode."""
        try:
            await self.coordinator.api.async_white_balance_control(mode=option)
        except Exception as err:
            _LOGGER.error("Error setting white balance mode for %s: %s", self._device_id, err)
            raise


class ZowieboxSaturationControl(ZowieboxCameraControlEntity, NumberEntity):
    """Saturation control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Saturation"
        self._attr_unique_id = f"{device_id}_saturation"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current saturation level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("saturation", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set saturation level."""
        try:
            await self.coordinator.api.async_white_balance_control(saturation=int(value))
        except Exception as err:
            _LOGGER.error("Error setting saturation for %s: %s", self._device_id, err)
            raise


# Image Controls
class ZowieboxBrightnessControl(ZowieboxCameraControlEntity, NumberEntity):
    """Brightness control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Brightness"
        self._attr_unique_id = f"{device_id}_brightness"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current brightness level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("brightness", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set brightness level."""
        try:
            await self.coordinator.api.async_image_control(brightness=int(value))
        except Exception as err:
            _LOGGER.error("Error setting brightness for %s: %s", self._device_id, err)
            raise


class ZowieboxContrastControl(ZowieboxCameraControlEntity, NumberEntity):
    """Contrast control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Contrast"
        self._attr_unique_id = f"{device_id}_contrast"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current contrast level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("contrast", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set contrast level."""
        try:
            await self.coordinator.api.async_image_control(contrast=int(value))
        except Exception as err:
            _LOGGER.error("Error setting contrast for %s: %s", self._device_id, err)
            raise


class ZowieboxSharpnessControl(ZowieboxCameraControlEntity, NumberEntity):
    """Sharpness control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Sharpness"
        self._attr_unique_id = f"{device_id}_sharpness"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current sharpness level."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("sharpness", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set sharpness level."""
        try:
            await self.coordinator.api.async_image_control(sharpness=int(value))
        except Exception as err:
            _LOGGER.error("Error setting sharpness for %s: %s", self._device_id, err)
            raise


# Audio Controls
class ZowieboxAudioVolumeControl(ZowieboxCameraControlEntity, NumberEntity):
    """Audio volume control for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Audio Volume"
        self._attr_unique_id = f"{device_id}_audio_volume"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return current audio volume."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("audio_volume", 50)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set audio volume."""
        try:
            await self.coordinator.api.async_audio_control(volume=int(value))
        except Exception as err:
            _LOGGER.error("Error setting audio volume for %s: %s", self._device_id, err)
            raise


class ZowieboxAudioSwitch(ZowieboxCameraControlEntity, SwitchEntity):
    """Audio on/off switch for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Audio"
        self._attr_unique_id = f"{device_id}_audio"

    @property
    def is_on(self) -> bool | None:
        """Return true if audio is on."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("audio_enabled", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn audio on."""
        try:
            await self.coordinator.api.async_audio_control(switch=True)
        except Exception as err:
            _LOGGER.error("Error turning on audio for %s: %s", self._device_id, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn audio off."""
        try:
            await self.coordinator.api.async_audio_control(switch=False)
        except Exception as err:
            _LOGGER.error("Error turning off audio for %s: %s", self._device_id, err)
            raise


# Recording Controls
class ZowieboxRecordingSwitch(ZowieboxCameraControlEntity, SwitchEntity):
    """Recording on/off switch for camera."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Recording"
        self._attr_unique_id = f"{device_id}_recording"

    @property
    def is_on(self) -> bool | None:
        """Return true if recording is on."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("recording", False)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start recording."""
        try:
            await self.coordinator.api.async_recording_control(command="start")
        except Exception as err:
            _LOGGER.error("Error starting recording for %s: %s", self._device_id, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop recording."""
        try:
            await self.coordinator.api.async_recording_control(command="stop")
        except Exception as err:
            _LOGGER.error("Error stopping recording for %s: %s", self._device_id, err)
            raise


# Tally Controls
class ZowieboxTallyColorSelect(ZowieboxCameraControlEntity, SelectEntity):
    """Tally color selection."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Tally Color"
        self._attr_unique_id = f"{device_id}_tally_color"
        self._attr_options = ["off", "red", "green", "blue"]

    @property
    def current_option(self) -> str | None:
        """Return current tally color."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("tally_color", "off")
        return None

    async def async_select_option(self, option: str) -> None:
        """Set tally color."""
        try:
            await self.coordinator.api.async_tally_control(color_id=option)
        except Exception as err:
            _LOGGER.error("Error setting tally color for %s: %s", self._device_id, err)
            raise


class ZowieboxTallyModeSelect(ZowieboxCameraControlEntity, SelectEntity):
    """Tally mode selection."""

    def __init__(self, coordinator, device_id: str, name: str, device: dict[str, Any]) -> None:
        super().__init__(coordinator, device_id, name, device)
        self._attr_name = f"{name} Tally Mode"
        self._attr_unique_id = f"{device_id}_tally_mode"
        self._attr_options = ["auto", "manual"]

    @property
    def current_option(self) -> str | None:
        """Return current tally mode."""
        if not self.coordinator.data or "devices" not in self.coordinator.data:
            return None
        
        for device in self.coordinator.data["devices"]:
            if device.get("id") == self._device_id:
                return device.get("tally_mode", "auto")
        return None

    async def async_select_option(self, option: str) -> None:
        """Set tally mode."""
        try:
            await self.coordinator.api.async_tally_control(mode_id=option)
        except Exception as err:
            _LOGGER.error("Error setting tally mode for %s: %s", self._device_id, err)
            raise
