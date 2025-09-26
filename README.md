# Zowiebox Home Assistant Integration

A Home Assistant integration for Zowiebox devices, providing seamless control and monitoring of your Zowiebox ecosystem.

## Features

- **Device Discovery**: Automatically discovers and configures Zowietek devices
- **Multiple Entity Types**: Supports sensors, switches, lights, cameras, and specialized controls
- **Real-time Updates**: Live status updates from your Zowietek devices
- **Local Control**: Direct communication with your Zowietek hub
- **HACS Compatible**: Easy installation through HACS
- **Professional Camera Control**: Full PTZ, focus, exposure, and image control
- **Audio Management**: Audio volume and on/off control
- **Recording Control**: Start/stop recording functionality
- **Tally Light Control**: Professional tally light management
- **NDI Support**: Network Device Interface control

## Supported Device Types

- **Sensors**: Temperature, humidity, motion, and other sensor data
- **Switches**: On/off control for compatible devices
- **Lights**: Full lighting control including brightness and color temperature
- **Cameras**: Video streaming and camera control
- **PTZ Controls**: Pan, tilt, zoom control with speed settings
- **Focus Controls**: Manual and automatic focus with speed control
- **Exposure Controls**: Gain, shutter, exposure mode selection
- **White Balance**: Color temperature and saturation control
- **Image Controls**: Brightness, contrast, sharpness adjustment
- **Audio Controls**: Volume control and audio on/off
- **Recording Controls**: Start/stop recording functionality
- **Tally Controls**: Color and mode selection for tally lights

## Installation

### HACS Installation (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add this repository URL: `https://github.com/tyoder/ha-zowiebox`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "Zowiebox" and install it
8. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/zowiebox` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for **Zowiebox**
4. Enter your Zowietek hub details:
   - **Host**: IP address of your Zowietek hub
   - **Port**: Port number (default: 80)
5. Click **Submit**

## API Documentation

This integration expects the following API endpoints on your Zowietek hub:

### GET /api/status
Returns the overall status of the Zowietek system.

**Response:**
```json
{
  "status": "online",
  "version": "1.0.0",
  "uptime": 12345
}
```

### GET /api/devices
Returns a list of all connected devices.

**Response:**
```json
[
  {
    "id": "camera_001",
    "name": "Studio Camera",
    "type": "camera",
    "state": "on",
    "capabilities": ["ptz", "focus", "exposure", "white_balance", "image_control", "audio", "recording", "tally"],
    "model": "ZW-CAM-001",
    "pan_position": 0,
    "tilt_position": 0,
    "zoom_level": 1.0,
    "focus_level": 50,
    "gain": 50,
    "shutter_speed": 100,
    "exposure_mode": "auto",
    "white_balance_mode": "auto",
    "brightness": 50,
    "contrast": 50,
    "sharpness": 50,
    "audio_volume": 50,
    "audio_enabled": true,
    "recording": false,
    "tally_color": "off",
    "tally_mode": "auto"
  }
]
```

### Camera Control Endpoints

#### POST /api/ptz/control
Controls PTZ camera movement.

**Request:**
```json
{
  "pan": 45,
  "tilt": -30,
  "zoom": 2.5,
  "speed": 5
}
```

#### POST /api/focus/control
Controls camera focus settings.

**Request:**
```json
{
  "focus_mode": "manual",
  "focus_speed": 5,
  "focus_area": "center",
  "af_sensitivity": "medium"
}
```

#### POST /api/exposure/control
Controls camera exposure settings.

**Request:**
```json
{
  "mode": "manual",
  "gain": 60,
  "shutter": 120,
  "wdr": true,
  "ae_lock": false
}
```

#### POST /api/whitebalance/control
Controls camera white balance settings.

**Request:**
```json
{
  "mode": "manual",
  "rgain": 100,
  "bgain": 100,
  "saturation": 50
}
```

#### POST /api/image/control
Controls camera image settings.

**Request:**
```json
{
  "brightness": 60,
  "contrast": 70,
  "sharpness": 80,
  "gamma": 50
}
```

#### POST /api/audio/control
Controls camera audio settings.

**Request:**
```json
{
  "switch": true,
  "volume": 75,
  "codec": "aac",
  "bitrate": 128
}
```

#### POST /api/recording/control
Controls recording functionality.

**Request:**
```json
{
  "index": 0,
  "command": "start"
}
```

#### POST /api/tally/control
Controls tally light settings.

**Request:**
```json
{
  "color_id": "red",
  "mode_id": "manual",
  "switch": "on"
}
```

## Device Capabilities

### Camera Devices
- **PTZ Control**: Pan, tilt, zoom with speed control
- **Focus Control**: Manual and automatic focus with speed settings
- **Exposure Control**: Gain, shutter speed, exposure mode selection
- **White Balance**: Color temperature and saturation control
- **Image Control**: Brightness, contrast, sharpness adjustment
- **Audio Control**: Volume control and audio on/off
- **Recording Control**: Start/stop recording functionality
- **Tally Control**: Professional tally light management
- **Streaming**: Video stream access and control

### Light Devices
- **Basic Control**: On/off functionality
- **Brightness**: 0-100% brightness control
- **Color Temperature**: Warm to cool white adjustment
- **Color**: RGB color control (if supported)

### Switch Devices
- **On/Off Control**: Basic switching functionality
- **Power Monitoring**: Power consumption tracking (if supported)

### Sensor Devices
- **Status Monitoring**: Device status and health
- **Environmental Data**: Temperature, humidity, etc.
- **Motion Detection**: Motion sensor data

## Troubleshooting

### Connection Issues
- Verify the IP address and port of your Zowietek hub
- Check that the hub is accessible from your Home Assistant instance
- Ensure firewall rules allow communication on the specified port

### Device Not Appearing
- Restart Home Assistant after installation
- Check the Home Assistant logs for any error messages
- Verify the device is properly connected to your Zowietek hub

## Development

### Requirements
- Python 3.9+
- Home Assistant 2023.1+
- aiohttp 3.8.0+

### Local Development
1. Clone this repository
2. Copy the `custom_components/zowiebox` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Configure the integration through the UI

### Testing
Run the integration tests:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Open an issue on GitHub
- Check the Home Assistant community forums
- Review the API documentation for your Zowiebox hub

## Changelog

### Version 1.0.0
- Initial release
- Basic device discovery and control
- Support for sensors, switches, and lights
- HACS compatibility
