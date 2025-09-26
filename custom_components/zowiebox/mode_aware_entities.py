"""
Mode-aware entities that show/hide based on device mode (encoding vs decoding).
"""

import logging
from typing import Any
from homeassistant.components.select import SelectEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.camera import Camera
from .device_mode import ZowieboxModeAwareEntity
from .stream_manager import ZowieboxStreamSelect, ZowieboxStreamSensor, ZowieboxStreamCamera
from .decoder_controls import (
    ZowieboxResolutionSelect, ZowieboxCodecSelect, 
    ZowieboxBitrateNumber, ZowieboxFramerateNumber, ZowieboxStreamSwitch
)

_LOGGER = logging.getLogger(__name__)


class ZowieboxModeAwareStreamSelect(ZowieboxModeAwareEntity, SelectEntity):
    """Mode-aware stream selection entity."""

    def __init__(self, coordinator, entity_type: str = "stream_select") -> None:
        """Initialize the mode-aware stream select entity."""
        super().__init__(coordinator, entity_type)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_aware_stream"
        
        # Get configuration based on current mode
        config = self.get_entity_config()
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if not self.coordinator.data:
            return None
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Find the currently active output stream
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    return stream_data.get("name", f"Stream {stream_id}")
        elif mode == "decoding":
            # Find the currently active input source
            streamplay_streams = self.coordinator.data.get("streamplay_streams", [])
            for stream in streamplay_streams:
                if stream.get("switch") == 1:
                    return stream.get("name", "Unknown Input")
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available options based on current mode."""
        if not self.coordinator.data:
            return []
        
        mode = self.device_mode.current_mode
        options = []
        
        if mode == "encoding":
            # Show output streams
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("type") in ["main", "sub"]:
                    name = stream_data.get("name", f"Stream {stream_id}")
                    options.append(name)
            
            # Add RTSP streams
            rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
            for stream in rtsp_streams:
                if stream.get("switch") == 1:
                    name = stream.get("name", f"RTSP {stream.get('stream_id', 'unknown')}")
                    options.append(name)
        
        elif mode == "decoding":
            # Show input sources
            streamplay_streams = self.coordinator.data.get("streamplay_streams", [])
            for stream in streamplay_streams:
                name = stream.get("name", f"Input {stream.get('index', 'unknown')}")
                options.append(name)
            
            # Add NDI sources if available
            ndi_sources = self.coordinator.data.get("ndi_sources", [])
            for source in ndi_sources:
                name = source.get("name", f"NDI {source.get('id', 'unknown')}")
                options.append(name)
        
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option based on current mode."""
        if not self.coordinator.data:
            return
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Activate the selected output stream
            await self._activate_output_stream(option)
        elif mode == "decoding":
            # Activate the selected input source
            await self._activate_input_source(option)
        
        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def _activate_output_stream(self, option: str) -> None:
        """Activate the selected output stream."""
        try:
            # Find and activate the stream
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("name") == option:
                    await self.coordinator.api.async_set_output_info(
                        stream_id, "set_output_switch", {"switch": 1}
                    )
                    break
        except Exception as err:
            _LOGGER.error("Failed to activate output stream %s: %s", option, err)

    async def _activate_input_source(self, option: str) -> None:
        """Activate the selected input source."""
        try:
            # Find and activate the input source
            streamplay_streams = self.coordinator.data.get("streamplay_streams", [])
            for stream in streamplay_streams:
                if stream.get("name") == option:
                    await self.coordinator.api.async_publish_stream_info(
                        "streamplay", "set_streamplay_switch",
                        {"index": stream.get("index"), "switch": 1}
                    )
                    break
        except Exception as err:
            _LOGGER.error("Failed to activate input source %s: %s", option, err)


class ZowieboxModeAwareResolutionSelect(ZowieboxModeAwareEntity, SelectEntity):
    """Mode-aware resolution selection entity."""

    def __init__(self, coordinator, entity_type: str = "resolution_select") -> None:
        """Initialize the mode-aware resolution select entity."""
        super().__init__(coordinator, entity_type)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_aware_resolution"
        
        # Get configuration based on current mode
        config = self.get_entity_config()
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if not self.coordinator.data:
            return None
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get current output resolution
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    width = stream_data.get("width", 0)
                    height = stream_data.get("height", 0)
                    if width and height:
                        return f"{width}x{height}"
        elif mode == "decoding":
            # Get current input resolution
            streamplay_streams = self.coordinator.data.get("streamplay_streams", [])
            for stream in streamplay_streams:
                if stream.get("switch") == 1:
                    # Input resolution might be detected from the stream
                    return "Auto"  # Placeholder for input resolution detection
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available resolution options."""
        if not self.coordinator.data:
            return []
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get available output resolutions
            device_info = self.coordinator.data.get("device_info", {})
            resolution_list = device_info.get("resolution_list", [])
            
            options = []
            for resolution in resolution_list:
                width = resolution.get("width", 0)
                height = resolution.get("height", 0)
                if width and height:
                    options.append(f"{width}x{height}")
            return options
        
        elif mode == "decoding":
            # For decoding, we might have different input resolution options
            return ["Auto", "1920x1080", "1280x720", "640x360"]
        
        return []

    async def async_select_option(self, option: str) -> None:
        """Change the selected resolution."""
        if not self.coordinator.data:
            return
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Set output resolution
            try:
                width, height = option.split("x")
                width = int(width)
                height = int(height)
                
                # Find active stream and update resolution
                streams = self.coordinator.data.get("streams", {})
                for stream_id, stream_data in streams.items():
                    if stream_data.get("switch") == 1:
                        await self.coordinator.api.async_set_output_info(
                            stream_id, "set_resolution",
                            {"width": width, "height": height}
                        )
                        break
                
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to set resolution %s: %s", option, err)
        
        elif mode == "decoding":
            # Set input resolution (if supported)
            _LOGGER.info("Input resolution set to %s", option)


class ZowieboxModeAwareCodecSelect(ZowieboxModeAwareEntity, SelectEntity):
    """Mode-aware codec selection entity."""

    def __init__(self, coordinator, entity_type: str = "codec_select") -> None:
        """Initialize the mode-aware codec select entity."""
        super().__init__(coordinator, entity_type)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_aware_codec"
        
        # Get configuration based on current mode
        config = self.get_entity_config()
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if not self.coordinator.data:
            return None
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get current output codec
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    codec_info = stream_data.get("codec", {})
                    selected_id = codec_info.get("selected_id", 0)
                    codec_list = codec_info.get("codec_list", [])
                    if selected_id < len(codec_list):
                        return codec_list[selected_id]
        elif mode == "decoding":
            # For decoding, we might detect the input codec
            return "Auto"  # Placeholder for input codec detection
        
        return None

    @property
    def options(self) -> list[str]:
        """Return the available codec options."""
        if not self.coordinator.data:
            return []
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get available output codecs
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    codec_info = stream_data.get("codec", {})
                    return codec_info.get("codec_list", [])
        elif mode == "decoding":
            # For decoding, we might have different input codec options
            return ["Auto", "H.264", "H.265", "MJPEG"]
        
        return []

    async def async_select_option(self, option: str) -> None:
        """Change the selected codec."""
        if not self.coordinator.data:
            return
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Set output codec
            try:
                # Find codec index
                codec_list = self.options
                if option in codec_list:
                    codec_index = codec_list.index(option)
                    
                    # Find active stream and update codec
                    streams = self.coordinator.data.get("streams", {})
                    for stream_id, stream_data in streams.items():
                        if stream_data.get("switch") == 1:
                            await self.coordinator.api.async_set_output_info(
                                stream_id, "set_codec",
                                {"codec_id": codec_index}
                            )
                            break
                    
                    await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to set codec %s: %s", option, err)
        
        elif mode == "decoding":
            # Set input codec (if supported)
            _LOGGER.info("Input codec set to %s", option)


class ZowieboxModeAwareBitrateNumber(ZowieboxModeAwareEntity, NumberEntity):
    """Mode-aware bitrate number entity."""

    def __init__(self, coordinator, entity_type: str = "bitrate_number") -> None:
        """Initialize the mode-aware bitrate number entity."""
        super().__init__(coordinator, entity_type)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_aware_bitrate"
        
        # Get configuration based on current mode
        config = self.get_entity_config()
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        
        # Set bitrate limits
        self._attr_native_min_value = 100000  # 100 kbps
        self._attr_native_max_value = 50000000  # 50 Mbps
        self._attr_native_step = 100000  # 100 kbps steps
        self._attr_native_unit_of_measurement = "bps"

    @property
    def native_value(self) -> float | None:
        """Return the current bitrate value."""
        if not self.coordinator.data:
            return None
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get current output bitrate
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    return stream_data.get("bitrate", 0)
        elif mode == "decoding":
            # For decoding, we might detect the input bitrate
            return 0  # Placeholder for input bitrate detection
        
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the bitrate value."""
        if not self.coordinator.data:
            return
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Set output bitrate
            try:
                # Find active stream and update bitrate
                streams = self.coordinator.data.get("streams", {})
                for stream_id, stream_data in streams.items():
                    if stream_data.get("switch") == 1:
                        await self.coordinator.api.async_set_output_info(
                            stream_id, "set_bitrate",
                            {"bitrate": int(value)}
                        )
                        break
                
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to set bitrate %s: %s", value, err)
        
        elif mode == "decoding":
            # Set input bitrate (if supported)
            _LOGGER.info("Input bitrate set to %s", value)


class ZowieboxModeAwareFramerateNumber(ZowieboxModeAwareEntity, NumberEntity):
    """Mode-aware framerate number entity."""

    def __init__(self, coordinator, entity_type: str = "framerate_number") -> None:
        """Initialize the mode-aware framerate number entity."""
        super().__init__(coordinator, entity_type)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode_aware_framerate"
        
        # Get configuration based on current mode
        config = self.get_entity_config()
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        
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
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Get current output framerate
            streams = self.coordinator.data.get("streams", {})
            for stream_id, stream_data in streams.items():
                if stream_data.get("switch") == 1:
                    return stream_data.get("framerate", 0)
        elif mode == "decoding":
            # For decoding, we might detect the input framerate
            return 0  # Placeholder for input framerate detection
        
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the framerate value."""
        if not self.coordinator.data:
            return
        
        mode = self.device_mode.current_mode
        
        if mode == "encoding":
            # Set output framerate
            try:
                # Find active stream and update framerate
                streams = self.coordinator.data.get("streams", {})
                for stream_id, stream_data in streams.items():
                    if stream_data.get("switch") == 1:
                        await self.coordinator.api.async_set_output_info(
                            stream_id, "set_framerate",
                            {"framerate": value}
                        )
                        break
                
                await self.coordinator.async_request_refresh()
            except Exception as err:
                _LOGGER.error("Failed to set framerate %s: %s", value, err)
        
        elif mode == "decoding":
            # Set input framerate (if supported)
            _LOGGER.info("Input framerate set to %s", value)
