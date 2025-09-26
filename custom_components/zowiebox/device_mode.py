"""
Device mode detection and dynamic entity management for ZowieTek devices.
Determines if device is in encoding or decoding mode and shows relevant settings.
"""

import logging
from typing import Any, Dict, List
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER
from .coordinator import ZowieboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ZowieboxDeviceMode:
    """Manages device mode detection and entity visibility."""
    
    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator):
        """Initialize device mode manager."""
        self.coordinator = coordinator
        self._current_mode = None
        self._mode_entities = {
            "encoding": [],
            "decoding": [],
            "common": []
        }
    
    @property
    def current_mode(self) -> str:
        """Get the current device mode."""
        if not self.coordinator.data:
            return "unknown"
        
        # Check if device is in encoding mode
        if self._is_encoding_mode():
            return "encoding"
        elif self._is_decoding_mode():
            return "decoding"
        else:
            return "unknown"
    
    def _is_encoding_mode(self) -> bool:
        """Check if device is in encoding mode."""
        if not self.coordinator.data:
            return False
        
        # Check for active video encoders
        streams = self.coordinator.data.get("streams", {})
        for stream_id, stream_data in streams.items():
            if stream_data.get("switch") == 1 and stream_data.get("type") in ["main", "sub"]:
                return True
        
        # Check for active RTSP streams
        rtsp_streams = self.coordinator.data.get("rtsp_streams", [])
        for stream in rtsp_streams:
            if stream.get("switch") == 1:
                return True
        
        return False
    
    def _is_decoding_mode(self) -> bool:
        """Check if device is in decoding mode."""
        if not self.coordinator.data:
            return False
        
        # Check for active video decoders
        device_info = self.coordinator.data.get("device_info", {})
        vdec_list = device_info.get("vdec", [])
        
        # Check for active streamplay streams (external sources)
        streamplay_streams = self.coordinator.data.get("streamplay_streams", [])
        active_streamplay = any(stream.get("switch") == 1 for stream in streamplay_streams)
        
        # Check for active NDI sources
        ndi_sources = self.coordinator.data.get("ndi_sources", [])
        active_ndi = any(source.get("active") for source in ndi_sources)
        
        return len(vdec_list) > 0 or active_streamplay or active_ndi
    
    def get_relevant_entities(self) -> List[str]:
        """Get list of relevant entity types for current mode."""
        mode = self.current_mode
        
        if mode == "encoding":
            return [
                "stream_select",      # Choose active stream
                "resolution_select",  # Set output resolution
                "codec_select",       # Set output codec
                "bitrate_number",     # Set output bitrate
                "framerate_number",   # Set output framerate
                "stream_switch",      # Enable/disable streams
                "camera",            # View output streams
                "sensor"             # Monitor stream status
            ]
        elif mode == "decoding":
            return [
                "input_select",       # Choose input source
                "input_resolution",   # Set input resolution
                "input_codec",        # Set input codec
                "input_bitrate",      # Set input bitrate
                "input_framerate",    # Set input framerate
                "input_switch",       # Enable/disable inputs
                "camera",             # View input streams
                "sensor"              # Monitor input status
            ]
        else:
            # Show common entities when mode is unknown
            return [
                "device_info",        # Basic device information
                "network_status",     # Network connectivity
                "system_status"       # System health
            ]
    
    def should_show_entity(self, entity_type: str) -> bool:
        """Check if an entity should be shown based on current mode."""
        relevant_entities = self.get_relevant_entities()
        return entity_type in relevant_entities
    
    def get_entity_config(self, entity_type: str) -> Dict[str, Any]:
        """Get configuration for an entity based on current mode."""
        mode = self.current_mode
        
        if entity_type == "stream_select" and mode == "encoding":
            return {
                "name": "Active Output Stream",
                "icon": "mdi:video-switch",
                "description": "Choose which stream to output"
            }
        elif entity_type == "input_select" and mode == "decoding":
            return {
                "name": "Active Input Source",
                "icon": "mdi:video-input-hdmi",
                "description": "Choose which input source to decode"
            }
        elif entity_type == "resolution_select" and mode == "encoding":
            return {
                "name": "Output Resolution",
                "icon": "mdi:monitor",
                "description": "Set the output video resolution"
            }
        elif entity_type == "input_resolution" and mode == "decoding":
            return {
                "name": "Input Resolution",
                "icon": "mdi:monitor-arrow-down",
                "description": "Set the input video resolution"
            }
        elif entity_type == "codec_select" and mode == "encoding":
            return {
                "name": "Output Codec",
                "icon": "mdi:code-braces",
                "description": "Set the output video codec"
            }
        elif entity_type == "input_codec" and mode == "decoding":
            return {
                "name": "Input Codec",
                "icon": "mdi:code-braces",
                "description": "Set the input video codec"
            }
        elif entity_type == "bitrate_number" and mode == "encoding":
            return {
                "name": "Output Bitrate",
                "icon": "mdi:speedometer",
                "description": "Set the output video bitrate"
            }
        elif entity_type == "input_bitrate" and mode == "decoding":
            return {
                "name": "Input Bitrate",
                "icon": "mdi:speedometer",
                "description": "Set the input video bitrate"
            }
        elif entity_type == "framerate_number" and mode == "encoding":
            return {
                "name": "Output Framerate",
                "icon": "mdi:filmstrip",
                "description": "Set the output video framerate"
            }
        elif entity_type == "input_framerate" and mode == "decoding":
            return {
                "name": "Input Framerate",
                "icon": "mdi:filmstrip",
                "description": "Set the input video framerate"
            }
        elif entity_type == "stream_switch" and mode == "encoding":
            return {
                "name": "Output Stream",
                "icon": "mdi:video",
                "description": "Enable/disable output stream"
            }
        elif entity_type == "input_switch" and mode == "decoding":
            return {
                "name": "Input Source",
                "icon": "mdi:video-input-hdmi",
                "description": "Enable/disable input source"
            }
        elif entity_type == "camera":
            if mode == "encoding":
                return {
                    "name": "Output Stream",
                    "icon": "mdi:video",
                    "description": "View the output stream"
                }
            elif mode == "decoding":
                return {
                    "name": "Input Stream",
                    "icon": "mdi:video-input-hdmi",
                    "description": "View the input stream"
                }
        elif entity_type == "sensor":
            if mode == "encoding":
                return {
                    "name": "Stream Status",
                    "icon": "mdi:chart-line",
                    "description": "Monitor output stream status"
                }
            elif mode == "decoding":
                return {
                    "name": "Input Status",
                    "icon": "mdi:chart-line",
                    "description": "Monitor input stream status"
                }
        
        # Default configuration
        return {
            "name": f"{entity_type.replace('_', ' ').title()}",
            "icon": "mdi:cog",
            "description": f"Control {entity_type.replace('_', ' ')}"
        }


class ZowieboxModeAwareEntity(CoordinatorEntity):
    """Base class for mode-aware entities."""
    
    def __init__(self, coordinator: ZowieboxDataUpdateCoordinator, entity_type: str):
        """Initialize mode-aware entity."""
        super().__init__(coordinator)
        self.entity_type = entity_type
        self.device_mode = ZowieboxDeviceMode(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=f"Zowietek {coordinator.entry.data['host']}",
            manufacturer=MANUFACTURER,
        )
    
    @property
    def available(self) -> bool:
        """Return if entity is available based on device mode."""
        if not super().available:
            return False
        
        return self.device_mode.should_show_entity(self.entity_type)
    
    @property
    def entity_registry_visible_default(self) -> bool:
        """Return if entity should be visible by default."""
        return self.device_mode.should_show_entity(self.entity_type)
    
    def get_entity_config(self) -> Dict[str, Any]:
        """Get entity configuration based on current mode."""
        return self.device_mode.get_entity_config(self.entity_type)
