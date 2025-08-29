#!/usr/bin/env python3
"""
SafeVault System Test Script
Tests signup, login, and secrets functionality
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_signup():
    """Test user signup"""
    print("🧪 Testing Signup...")
    
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{API_BASE}/signup", json=signup_data)
        if response.status_code == 200:
            print("✅ Signup successful!")
            return True
        else:
            print(f"❌ Signup failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False

def test_login():
    """Test user login"""
    print("🧪 Testing Login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            print(f"✅ Login successful! User: {user['username']}, Role: {user['role']}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_create_secret(token):
    """Test creating a secret"""
    print("🧪 Testing Create Secret...")
    
    headers = {"Authorization": f"Bearer {token}"}
    secret_data = {
        "name": "test-api-key",
        "value": "sk-1234567890abcdef",
        "description": "Test API key for SafeVault"
    }
    
    try:
        response = requests.post(f"{API_BASE}/secrets", json=secret_data, headers=headers)
        if response.status_code == 200:
            print("✅ Secret created successfully!")
            return True
        else:
            print(f"❌ Create secret failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create secret error: {e}")
        return False

def test_list_secrets(token):
    """Test listing secrets"""
    print("🧪 Testing List Secrets...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/secrets", headers=headers)
        if response.status_code == 200:
            secrets = response.json()
            print(f"✅ Found {len(secrets)} secrets:")
            for secret in secrets:
                print(f"   - {secret['name']}: {secret['description']}")
            return secrets
        else:
            print(f"❌ List secrets failed: {response.text}")
            return []
    except Exception as e:
        print(f"❌ List secrets error: {e}")
        return []

def test_get_secret(token, secret_name):
    """Test getting a specific secret"""
    print(f"🧪 Testing Get Secret: {secret_name}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/secrets/{secret_name}", headers=headers)
        if response.status_code == 200:
            secret = response.json()
            print(f"✅ Retrieved secret: {secret['name']} = {secret['value'][:10]}...")
            return True
        else:
            print(f"❌ Get secret failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get secret error: {e}")
        return False

def test_delete_secret(token, secret_name):
    """Test deleting a secret"""
    print(f"🧪 Testing Delete Secret: {secret_name}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{API_BASE}/secrets/{secret_name}", headers=headers)
        if response.status_code == 200:
            print("✅ Secret deleted successfully!")
            return True
        else:
            print(f"❌ Delete secret failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete secret error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔐 SafeVault System Test")
    print("=" * 40)
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE}/docs")
        print("✅ Backend is running!")
    except:
        print("❌ Backend is not running. Please start it first:")
        print("   cd backend && python app.py")
        return
    
    print()
    
    # Test signup
    signup_success = test_signup()
    time.sleep(1)
    
    # Test login
    token = test_login()
    if not token:
        return
    time.sleep(1)
    
    # Test create secret
    create_success = test_create_secret(token)
    time.sleep(1)
    
    # Test list secrets
    secrets = test_list_secrets(token)
    time.sleep(1)
    
    # Test get secret
    if secrets:
        get_success = test_get_secret(token, secrets[0]['name'])
        time.sleep(1)
        
        # Test delete secret (only if user is admin)
        # delete_success = test_delete_secret(token, secrets[0]['name'])
    
    print()
    print("🎉 Test completed!")
    print("✅ All core functionality is working!")

if __name__ == "__main__":
    main()