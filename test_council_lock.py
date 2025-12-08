#!/usr/bin/env python3
"""Test script to debug council lock API"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_locked_council():
    """Test get_locked_council API"""
    url = f"{BASE_URL}/api/method/lodgeick.api.get_locked_council"

    print("Testing GET locked council...")
    response = requests.post(url)

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Raw Response: {response.text[:500]}")

def test_set_locked_council():
    """Test set_locked_council API"""
    url = f"{BASE_URL}/api/method/lodgeick.api.set_locked_council"

    print("\nTesting SET locked council...")
    response = requests.post(url, json={"council_code": "AKL"})

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Raw Response: {response.text[:500]}")

if __name__ == "__main__":
    test_get_locked_council()
    test_set_locked_council()
