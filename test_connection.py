#!/usr/bin/env python3
"""
Test script to debug Zowietek device connection.
Run this script to test your Zowietek device connectivity.
"""

import asyncio
import aiohttp
import sys
import json
from typing import Dict, Any

async def test_connection(host: str, port: int = 80) -> None:
    """Test connection to Zowietek device."""
    base_url = f"http://{host}:{port}"
    
    print(f"Testing connection to {base_url}")
    print("=" * 50)
    
    # Test ZowieTek API endpoints (based on documentation)
    endpoints_to_test = [
        "/",
        "/video?option=getinfo&login_check_flag=1",
        "/ptz?option=getinfo&login_check_flag=1",
        "/audio?option=getinfo&login_check_flag=1",
        "/stream?option=getinfo&login_check_flag=1",
        "/network?option=getinfo&login_check_flag=1",
        "/system?option=getinfo&login_check_flag=1",
        "/storage?option=getinfo&login_check_flag=1",
        "/record?option=getinfo&login_check_flag=1"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                print(f"Testing: {url}")
                
                # ZowieTek API uses POST requests with JSON payload
                if "?" in endpoint:
                    # This is a ZowieTek API endpoint, use POST
                    payload = {"group": "all"}
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        print(f"  Status: {response.status}")
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"  Response: {json.dumps(data, indent=2)}")
                            except:
                                text = await response.text()
                                print(f"  Response (text): {text[:200]}...")
                        else:
                            print(f"  Error: HTTP {response.status}")
                else:
                    # This is a basic HTTP endpoint, use GET
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        print(f"  Status: {response.status}")
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"  Response: {json.dumps(data, indent=2)}")
                            except:
                                text = await response.text()
                                print(f"  Response (text): {text[:200]}...")
                        elif response.status in [404, 405]:
                            print(f"  Endpoint exists but method not allowed")
                        else:
                            print(f"  Error: HTTP {response.status}")
            except asyncio.TimeoutError:
                print(f"  Timeout")
            except Exception as e:
                print(f"  Error: {e}")
            print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <host> [port]")
        print("Example: python test_connection.py 192.168.1.100")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    
    asyncio.run(test_connection(host, port))
