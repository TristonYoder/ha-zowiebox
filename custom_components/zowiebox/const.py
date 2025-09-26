"""Constants for the Zowiebox integration."""

DOMAIN = "zowiebox"
MANUFACTURER = "Zowiebox"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"

# Default values
DEFAULT_PORT = 80
DEFAULT_TIMEOUT = 10

# ZowieTek API endpoints (based on official documentation)
API_ENDPOINT_VIDEO = "/video"
API_ENDPOINT_PTZ = "/ptz"
API_ENDPOINT_AUDIO = "/audio"
API_ENDPOINT_STREAM = "/stream"
API_ENDPOINT_STREAMPLAY = "/streamplay"
API_ENDPOINT_NETWORK = "/network"
API_ENDPOINT_SYSTEM = "/system"
API_ENDPOINT_STORAGE = "/storage"
API_ENDPOINT_RECORD = "/record"

# Common API parameters
LOGIN_CHECK_FLAG = "login_check_flag=1"
OPTION_GET = "option=getinfo"
OPTION_SET = "option=setinfo"

# Zowietek-specific endpoints
API_ENDPOINT_CAMERA_INFO = "/api/camera/info"
API_ENDPOINT_PTZ_CONTROL = "/api/ptz/control"
API_ENDPOINT_FOCUS_CONTROL = "/api/focus/control"
API_ENDPOINT_ZOOM_CONTROL = "/api/zoom/control"
API_ENDPOINT_EXPOSURE_CONTROL = "/api/exposure/control"
API_ENDPOINT_WHITE_BALANCE = "/api/whitebalance/control"
API_ENDPOINT_IMAGE_CONTROL = "/api/image/control"
API_ENDPOINT_AUDIO_CONTROL = "/api/audio/control"
API_ENDPOINT_STREAM_CONTROL = "/api/stream/control"
API_ENDPOINT_RECORDING_CONTROL = "/api/recording/control"
API_ENDPOINT_TALLY_CONTROL = "/api/tally/control"
API_ENDPOINT_NDI_CONTROL = "/api/ndi/control"
API_ENDPOINT_DEVICE_CONTROL = "/api/device/control"

# Device types
DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_PTZ = "ptz"
DEVICE_TYPE_STREAM = "stream"
DEVICE_TYPE_RECORDING = "recording"

# Camera capabilities
CAPABILITY_PTZ = "ptz"
CAPABILITY_FOCUS = "focus"
CAPABILITY_ZOOM = "zoom"
CAPABILITY_EXPOSURE = "exposure"
CAPABILITY_WHITE_BALANCE = "white_balance"
CAPABILITY_IMAGE_CONTROL = "image_control"
CAPABILITY_AUDIO = "audio"
CAPABILITY_STREAMING = "streaming"
CAPABILITY_RECORDING = "recording"
CAPABILITY_TALLY = "tally"
CAPABILITY_NDI = "ndi"

# Update intervals
UPDATE_INTERVAL = 30  # seconds
