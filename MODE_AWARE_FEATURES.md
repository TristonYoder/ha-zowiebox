# ZowieTek Mode-Aware Integration Features

## 🎯 **Intelligent Entity Management**

The ZowieTek integration now features **mode-aware entities** that automatically show/hide based on your device's current operation mode. This provides a cleaner, more intuitive interface that only displays relevant controls.

## 🔄 **Device Mode Detection**

### **Encoding Mode** 📤
When your ZowieTek device is **outputting streams** (encoding):
- **Shows**: Output stream controls, resolution settings, codec selection, bitrate control
- **Hides**: Input source controls, decoding-specific settings
- **Focus**: Stream quality, output configuration, broadcasting settings

### **Decoding Mode** 📥
When your ZowieTek device is **receiving streams** (decoding):
- **Shows**: Input source selection, input quality settings, decoding controls
- **Hides**: Output stream controls, encoding-specific settings
- **Focus**: Input source management, decoding configuration, display settings

### **Unknown Mode** ❓
When the device mode cannot be determined:
- **Shows**: Basic device information, network status, system health
- **Hides**: Mode-specific controls
- **Focus**: Device connectivity and basic information

## 📱 **Mode-Aware Entities**

### **Encoding Mode Entities**

#### **Stream Selection**
- **Entity**: `select.mode_aware_stream`
- **Name**: "Active Output Stream"
- **Icon**: `mdi:video-switch`
- **Purpose**: Choose which stream to output
- **Options**: Main Stream, Sub Stream, RTSP Streams, SRT Streams

#### **Resolution Control**
- **Entity**: `select.mode_aware_resolution`
- **Name**: "Output Resolution"
- **Icon**: `mdi:monitor`
- **Purpose**: Set the output video resolution
- **Options**: 4K, 1440p, 1080p, 720p, 360p, 180p

#### **Codec Selection**
- **Entity**: `select.mode_aware_codec`
- **Name**: "Output Codec"
- **Icon**: `mdi:code-braces`
- **Purpose**: Set the output video codec
- **Options**: H.264, H.265, MJPEG

#### **Bitrate Control**
- **Entity**: `number.mode_aware_bitrate`
- **Name**: "Output Bitrate"
- **Icon**: `mdi:speedometer`
- **Purpose**: Set the output video bitrate
- **Range**: 100 kbps to 50 Mbps

#### **Framerate Control**
- **Entity**: `number.mode_aware_framerate`
- **Name**: "Output Framerate"
- **Icon**: `mdi:filmstrip`
- **Purpose**: Set the output video framerate
- **Range**: 1.0 to 60.0 fps

### **Decoding Mode Entities**

#### **Input Selection**
- **Entity**: `select.mode_aware_stream`
- **Name**: "Active Input Source"
- **Icon**: `mdi:video-input-hdmi`
- **Purpose**: Choose which input source to decode
- **Options**: Streamplay sources, NDI sources, external inputs

#### **Input Resolution**
- **Entity**: `select.mode_aware_resolution`
- **Name**: "Input Resolution"
- **Icon**: `mdi:monitor-arrow-down`
- **Purpose**: Set the input video resolution
- **Options**: Auto, 1920x1080, 1280x720, 640x360

#### **Input Codec**
- **Entity**: `select.mode_aware_codec`
- **Name**: "Input Codec"
- **Icon**: `mdi:code-braces`
- **Purpose**: Set the input video codec
- **Options**: Auto, H.264, H.265, MJPEG

#### **Input Bitrate**
- **Entity**: `number.mode_aware_bitrate`
- **Name**: "Input Bitrate"
- **Icon**: `mdi:speedometer`
- **Purpose**: Set the input video bitrate
- **Range**: 100 kbps to 50 Mbps

#### **Input Framerate**
- **Entity**: `number.mode_aware_framerate`
- **Name**: "Input Framerate"
- **Icon**: `mdi:filmstrip`
- **Purpose**: Set the input video framerate
- **Range**: 1.0 to 60.0 fps

## 🎨 **Dynamic Interface Benefits**

### **Cleaner Interface**
- **No Clutter**: Only relevant controls are shown
- **Context-Aware**: Controls match your current use case
- **Intuitive**: Easy to understand what each control does

### **Better User Experience**
- **Focused Controls**: No confusion about which settings to use
- **Mode-Specific Names**: Clear indication of what each control affects
- **Appropriate Icons**: Visual cues that match the current mode

### **Professional Workflow**
- **Encoding Workflow**: Perfect for content creators and broadcasters
- **Decoding Workflow**: Ideal for receiving and displaying content
- **Automatic Switching**: No manual mode selection required

## 🔧 **Technical Implementation**

### **Mode Detection Logic**
```python
def _is_encoding_mode(self) -> bool:
    """Check if device is in encoding mode."""
    # Check for active video encoders
    # Check for active RTSP streams
    # Check for active SRT streams
    return has_active_outputs

def _is_decoding_mode(self) -> bool:
    """Check if device is in decoding mode."""
    # Check for active video decoders
    # Check for active streamplay streams
    # Check for active NDI sources
    return has_active_inputs
```

### **Entity Visibility**
```python
@property
def available(self) -> bool:
    """Return if entity is available based on device mode."""
    return self.device_mode.should_show_entity(self.entity_type)
```

### **Dynamic Configuration**
```python
def get_entity_config(self) -> Dict[str, Any]:
    """Get entity configuration based on current mode."""
    mode = self.device_mode.current_mode
    
    if mode == "encoding":
        return {"name": "Output Stream", "icon": "mdi:video"}
    elif mode == "decoding":
        return {"name": "Input Source", "icon": "mdi:video-input-hdmi"}
```

## 📋 **Usage Examples**

### **Encoding Scenario**
When you're **broadcasting** or **streaming content**:
1. **Active Output Stream**: Choose "Main Stream" for high quality
2. **Output Resolution**: Set to "1920x1080" for 1080p
3. **Output Codec**: Select "H.264" for compatibility
4. **Output Bitrate**: Set to 5000000 (5 Mbps) for quality
5. **Output Framerate**: Set to 30.0 fps for smooth playback

### **Decoding Scenario**
When you're **receiving** or **displaying content**:
1. **Active Input Source**: Choose "IPTV Channel" or "NDI Source"
2. **Input Resolution**: Set to "Auto" for automatic detection
3. **Input Codec**: Select "Auto" for automatic detection
4. **Input Bitrate**: Set to 0 for automatic detection
5. **Input Framerate**: Set to 0 for automatic detection

### **Dashboard Configuration**
```yaml
# Encoding Mode Dashboard
type: vertical-stack
cards:
  - type: entities
    title: "Output Stream Control"
    entities:
      - select.mode_aware_stream
      - select.mode_aware_resolution
      - select.mode_aware_codec
      - number.mode_aware_bitrate
      - number.mode_aware_framerate

# Decoding Mode Dashboard
type: vertical-stack
cards:
  - type: entities
    title: "Input Source Control"
    entities:
      - select.mode_aware_stream
      - select.mode_aware_resolution
      - select.mode_aware_codec
      - number.mode_aware_bitrate
      - number.mode_aware_framerate
```

## 🚀 **Benefits**

### **For Content Creators**
- **Streaming Setup**: Easy configuration for live streaming
- **Quality Control**: Precise control over output quality
- **Professional Workflow**: Industry-standard controls

### **For System Integrators**
- **Clean Interface**: No confusing or irrelevant controls
- **Mode-Specific Workflows**: Tailored for specific use cases
- **Automatic Detection**: No manual configuration required

### **For Home Assistant Users**
- **Intuitive Controls**: Easy to understand and use
- **Context-Aware**: Controls match your current needs
- **Professional Features**: Access to advanced streaming controls

## 🔄 **Mode Switching**

The integration automatically detects mode changes and updates the interface accordingly:

1. **Start Encoding**: Begin outputting streams → Interface switches to encoding mode
2. **Start Decoding**: Begin receiving streams → Interface switches to decoding mode
3. **Stop All**: No active streams → Interface shows basic device information

## 📊 **Entity Summary**

| Mode | Stream Selection | Resolution | Codec | Bitrate | Framerate |
|------|------------------|------------|-------|---------|-----------|
| **Encoding** | Output Stream | Output Resolution | Output Codec | Output Bitrate | Output Framerate |
| **Decoding** | Input Source | Input Resolution | Input Codec | Input Bitrate | Input Framerate |
| **Unknown** | Hidden | Hidden | Hidden | Hidden | Hidden |

This mode-aware system provides a **professional, intuitive interface** that adapts to your specific use case, making the ZowieTek integration more powerful and user-friendly than ever! 🎉
