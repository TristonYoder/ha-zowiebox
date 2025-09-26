# ZowieTek Home Assistant Integration - Features

## 🎯 **Stream Management & Control**

### **1. Active Stream Selection**
- **Single Select Entity**: Choose which stream is currently active
- **Automatic Discovery**: All available streams are automatically detected
- **Stream Types**: Main, Sub, RTSP, and SRT streams

### **2. Stream Configuration Controls**

#### **Resolution Control**
- **Select Entity**: Choose from available resolutions (4K, 1080p, 720p, etc.)
- **Dynamic Options**: Automatically populated from device capabilities
- **Per-Stream**: Each stream can have different resolution settings

#### **Codec Control**
- **Select Entity**: Choose video codec (H.264, H.265, MJPEG)
- **Profile Selection**: BP, MP, HP profiles available
- **Rate Control**: CBR/VBR options

#### **Bitrate Control**
- **Number Entity**: Set bitrate from 100 kbps to 50 Mbps
- **Real-time Adjustment**: Changes apply immediately
- **Per-Stream**: Individual bitrate control for each stream

#### **Framerate Control**
- **Number Entity**: Set framerate from 1.0 to 60.0 fps
- **Precise Control**: 0.1 fps increments
- **Per-Stream**: Individual framerate control

### **3. Stream Status & Monitoring**

#### **Stream Status Sensors**
- **Active/Inactive Status**: Real-time stream status
- **Stream Information**: Resolution, codec, bitrate, framerate
- **Stream URLs**: RTSP and SRT stream URLs
- **Per-Stream**: Individual status for each stream

#### **Stream Switches**
- **Enable/Disable**: Turn streams on/off individually
- **Quick Control**: Easy stream management
- **Per-Stream**: Individual control for each stream

### **4. Camera Integration**

#### **Stream Cameras**
- **Live Viewing**: View streams directly in Home Assistant
- **Snapshot Support**: Get still images from streams
- **Multiple Streams**: Separate camera entity for each stream
- **RTSP Integration**: Direct RTSP stream viewing

## 🔧 **Device Capabilities**

### **Supported Stream Types**
- **Main Stream**: Primary high-quality stream
- **Sub Stream**: Secondary lower-quality stream
- **RTSP Streams**: Real-time streaming protocol
- **SRT Streams**: Secure reliable transport

### **Video Capabilities**
- **Resolutions**: 4K (3840x2160), 1440p, 1080p, 720p, 360p
- **Codecs**: H.264, H.265, MJPEG
- **Profiles**: BP (Baseline), MP (Main), HP (High)
- **Rate Control**: CBR (Constant), VBR (Variable)

### **Audio Capabilities**
- **Codecs**: AAC, MP3, G.711A
- **Sample Rates**: 8kHz to 48kHz
- **Bitrates**: 32kbps to 256kbps
- **Channels**: Stereo (2-channel)

## 📱 **Home Assistant Entities**

### **Select Entities**
- `select.active_stream` - Choose active stream
- `select.stream_0_resolution` - Main stream resolution
- `select.stream_1_resolution` - Sub stream resolution
- `select.stream_0_codec` - Main stream codec
- `select.stream_1_codec` - Sub stream codec

### **Number Entities**
- `number.stream_0_bitrate` - Main stream bitrate (bps)
- `number.stream_1_bitrate` - Sub stream bitrate (bps)
- `number.stream_0_framerate` - Main stream framerate (fps)
- `number.stream_1_framerate` - Sub stream framerate (fps)

### **Switch Entities**
- `switch.stream_0` - Main stream on/off
- `switch.stream_1` - Sub stream on/off

### **Sensor Entities**
- `sensor.stream_0_status` - Main stream status
- `sensor.stream_1_status` - Sub stream status

### **Camera Entities**
- `camera.stream_0` - Main stream camera
- `camera.stream_1` - Sub stream camera

## 🚀 **Usage Examples**

### **Automation Examples**

#### **Switch to High Quality for Recording**
```yaml
automation:
  - alias: "Switch to High Quality for Recording"
    trigger:
      - platform: state
        entity_id: binary_sensor.recording_active
        to: "on"
    action:
      - service: select.select_option
        target:
          entity_id: select.active_stream
        data:
          option: "Main Stream"
      - service: select.select_option
        target:
          entity_id: select.stream_0_resolution
        data:
          option: "1920x1080"
```

#### **Optimize for Low Bandwidth**
```yaml
automation:
  - alias: "Optimize for Low Bandwidth"
    trigger:
      - platform: numeric_state
        entity_id: sensor.network_bandwidth
        below: 1000000  # 1 Mbps
    action:
      - service: select.select_option
        target:
          entity_id: select.active_stream
        data:
          option: "Sub Stream"
      - service: number.set_value
        target:
          entity_id: number.stream_1_bitrate
        data:
          value: 500000  # 500 kbps
```

### **Dashboard Cards**

#### **Stream Control Card**
```yaml
type: vertical-stack
cards:
  - type: entities
    title: "Stream Control"
    entities:
      - select.active_stream
      - switch.stream_0
      - switch.stream_1
  - type: entities
    title: "Main Stream Settings"
    entities:
      - select.stream_0_resolution
      - select.stream_0_codec
      - number.stream_0_bitrate
      - number.stream_0_framerate
  - type: entities
    title: "Sub Stream Settings"
    entities:
      - select.stream_1_resolution
      - select.stream_1_codec
      - number.stream_1_bitrate
      - number.stream_1_framerate
```

#### **Stream Status Card**
```yaml
type: entities
title: "Stream Status"
entities:
  - sensor.stream_0_status
  - sensor.stream_1_status
  - camera.stream_0
  - camera.stream_1
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Stream Not Available**
- Check if the stream is enabled in the switch entity
- Verify the stream configuration in the select entities
- Check the device logs for API errors

#### **Poor Video Quality**
- Increase bitrate using the number entity
- Switch to a higher resolution
- Check network bandwidth

#### **Stream Not Loading**
- Verify RTSP URLs are correct
- Check network connectivity
- Ensure the stream is active

### **Debug Information**
- Check Home Assistant logs for detailed error messages
- Use the sensor entities to monitor stream status
- Verify device connectivity with the test script

## 📋 **Configuration**

### **Required Configuration**
- **Host**: ZowieTek device IP address
- **Port**: Device port (default: 80)

### **Optional Configuration**
- **Update Interval**: How often to refresh data (default: 30 seconds)
- **Timeout**: API request timeout (default: 10 seconds)

### **Advanced Configuration**
- **Custom Stream Names**: Modify stream names in the device
- **Stream Priorities**: Set which streams are active by default
- **Quality Profiles**: Create preset quality configurations

## 🎉 **Benefits**

### **For Home Assistant Users**
- **Unified Control**: Manage all streams from one interface
- **Automation Ready**: Full Home Assistant automation support
- **Real-time Monitoring**: Live stream status and information
- **Flexible Configuration**: Granular control over all settings

### **For ZowieTek Users**
- **Easy Integration**: Simple setup in Home Assistant
- **Professional Control**: Access to all device features
- **Remote Management**: Control streams from anywhere
- **Automation**: Intelligent stream management

This integration provides complete control over your ZowieTek device's streaming capabilities, making it easy to manage multiple streams, adjust quality settings, and integrate with your Home Assistant automation system.
