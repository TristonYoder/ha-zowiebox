"""Tests for Zowiebox API client."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.zowiebox.api import ZowieboxAPI


@pytest.fixture
def api():
    """Create API client for testing."""
    return ZowieboxAPI("192.168.1.100", 80, "user", "pass")


@pytest.mark.asyncio
async def test_api_initialization(api):
    """Test API client initialization."""
    assert api._host == "192.168.1.100"
    assert api._port == 80
    assert api._username == "user"
    assert api._password == "pass"
    assert api.base_url == "http://192.168.1.100:80"


@pytest.mark.asyncio
async def test_get_session(api):
    """Test session creation."""
    session = await api._get_session()
    assert session is not None
    await api.close()


@pytest.mark.asyncio
async def test_async_get_status(api):
    """Test getting status."""
    mock_response = {"status": "online", "version": "1.0.0"}
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.raise_for_status = AsyncMock()
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value = mock_response_obj
        
        result = await api.async_get_status()
        assert result == mock_response


@pytest.mark.asyncio
async def test_async_get_devices(api):
    """Test getting devices."""
    mock_devices = [
        {"id": "device_001", "name": "Test Device", "type": "light", "state": "on"}
    ]
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.raise_for_status = AsyncMock()
        mock_response_obj.json = AsyncMock(return_value=mock_devices)
        mock_get.return_value.__aenter__.return_value = mock_response_obj
        
        result = await api.async_get_devices()
        assert result == mock_devices


@pytest.mark.asyncio
async def test_async_control_device(api):
    """Test controlling a device."""
    mock_response = {"success": True, "message": "Device controlled"}
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response_obj = AsyncMock()
        mock_response_obj.raise_for_status = AsyncMock()
        mock_response_obj.json = AsyncMock(return_value=mock_response)
        mock_post.return_value.__aenter__.return_value = mock_response_obj
        
        result = await api.async_control_device("device_001", "turn_on", {"brightness": 80})
        assert result == mock_response
