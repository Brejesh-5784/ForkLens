#!/usr/bin/env python3

import os
import time
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "https://7f88bcac-ec6f-401a-a00a-e0e7fb537071.eu-west-1-0.aws.cloud.qdrant.io")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.gV3mlPS4tZYvIpx-qsxMD_UsEY8MZ9NFzVS8J7vtsT4")

print("🔍 QDRANT CONNECTION DIAGNOSIS")
print("=" * 50)

# Test 1: Basic URL accessibility
print("\n1️⃣ Testing URL accessibility...")
try:
    start_time = time.time()
    response = requests.get(f"{QDRANT_HOST}/", timeout=10)
    end_time = time.time()
    print(f"✅ URL accessible - Response: {response.status_code}")
    print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
except requests.exceptions.Timeout:
    print("❌ URL timeout - Server not responding")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - Cannot reach server")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: API endpoint with authentication
print("\n2️⃣ Testing API endpoint...")
try:
    start_time = time.time()
    headers = {"api-key": QDRANT_API_KEY}
    response = requests.get(f"{QDRANT_HOST}/collections", headers=headers, timeout=15)
    end_time = time.time()
    print(f"✅ API accessible - Response: {response.status_code}")
    print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
    if response.status_code == 200:
        print(f"📊 Response: {response.json()}")
except requests.exceptions.Timeout:
    print("❌ API timeout - Authentication/API issues")
except Exception as e:
    print(f"❌ API Error: {e}")

# Test 3: Qdrant client with different timeouts
print("\n3️⃣ Testing Qdrant client...")
for timeout in [10, 30, 60]:
    try:
        print(f"   Testing with {timeout}s timeout...")
        start_time = time.time()
        client = QdrantClient(
            url=QDRANT_HOST,
            api_key=QDRANT_API_KEY,
            timeout=timeout
        )
        collections = client.get_collections()
        end_time = time.time()
        print(f"   ✅ Success with {timeout}s timeout")
        print(f"   ⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"   📊 Collections: {[c.name for c in collections.collections]}")
        break
    except Exception as e:
        print(f"   ❌ Failed with {timeout}s timeout: {e}")

# Test 4: Network diagnostics
print("\n4️⃣ Network diagnostics...")
import socket
try:
    # Extract hostname from URL
    hostname = QDRANT_HOST.replace("https://", "").replace("http://", "")
    ip = socket.gethostbyname(hostname)
    print(f"✅ DNS Resolution: {hostname} → {ip}")
    
    # Test port connectivity
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((ip, 443))  # HTTPS port
    if result == 0:
        print("✅ Port 443 (HTTPS) is accessible")
    else:
        print("❌ Port 443 (HTTPS) is not accessible")
    sock.close()
except Exception as e:
    print(f"❌ Network error: {e}")

print("\n" + "=" * 50)
print("🔧 RECOMMENDATIONS:")
print("1. Check your internet connection speed")
print("2. Try using a VPN if behind corporate firewall")
print("3. Verify Qdrant cloud instance is running in dashboard")
print("4. Check if API key is still valid")
print("5. Consider switching to a different Qdrant region")