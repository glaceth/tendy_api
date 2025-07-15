#!/usr/bin/env python3
"""
Test script for Tendy API live data fetching and analysis
"""

import json
import requests
import time
from datetime import datetime

# Test data - sample token
TEST_TOKEN = {
    "token_address": "0x1234567890abcdef1234567890abcdef12345678",
    "name": "Test Token",
    "symbol": "TEST",
    "mc": 1000000,
    "holders": 1000,
    "rugscore": 3.5,
    "honeypot": False,
    "lp_locked": True,
    "top_holders": ["0xabc123", "0xdef456"],
    "timestamp": datetime.now().isoformat()
}

def test_token_storage():
    """Test token storage and retrieval"""
    print("🧪 Testing token storage...")
    
    # Save test token
    with open("tokens.json", "w") as f:
        json.dump([TEST_TOKEN], f, indent=2)
    
    # Load and verify
    with open("tokens.json", "r") as f:
        tokens = json.load(f)
    
    assert len(tokens) == 1
    assert tokens[0]["symbol"] == "TEST"
    print("✅ Token storage test passed")

def test_history_storage():
    """Test analysis history storage"""
    print("🧪 Testing history storage...")
    
    # Create test history
    history = {
        TEST_TOKEN["token_address"]: [
            {
                "timestamp": datetime.now().isoformat(),
                "token_data": TEST_TOKEN,
                "analysis": "Test analysis",
                "evolution": {}
            }
        ]
    }
    
    # Save history
    with open("analyses_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
    # Load and verify
    with open("analyses_history.json", "r") as f:
        loaded_history = json.load(f)
    
    assert TEST_TOKEN["token_address"] in loaded_history
    assert len(loaded_history[TEST_TOKEN["token_address"]]) == 1
    print("✅ History storage test passed")

def test_evolution_comparison():
    """Test evolution data comparison"""
    print("🧪 Testing evolution comparison...")
    
    from analyze_with_gpt import format_evolution_data
    
    # Create current and previous data
    current_data = TEST_TOKEN.copy()
    current_data["mc"] = 1500000  # 50% increase
    current_data["holders"] = 1200  # 20% increase
    current_data["rugscore"] = 4.0  # 0.5 increase
    
    previous_data = TEST_TOKEN.copy()
    
    # Test evolution formatting
    evolution = format_evolution_data(current_data, previous_data)
    
    assert "Market Cap" in evolution
    assert "50.0%" in evolution["Market Cap"]
    assert "Holders" in evolution
    assert "20.0%" in evolution["Holders"]
    print("✅ Evolution comparison test passed")

def test_api_import():
    """Test API import and basic functionality"""
    print("🧪 Testing API import...")
    
    # This will also start the periodic analysis thread
    import tendy_api
    
    # Test basic functions
    tokens = tendy_api.load_tokens()
    history = tendy_api.load_analyses_history()
    
    print(f"Loaded {len(tokens)} tokens")
    print(f"Loaded history for {len(history)} tokens")
    print("✅ API import test passed")

def main():
    """Run all tests"""
    print("🚀 Starting Tendy API tests...")
    
    test_token_storage()
    test_history_storage()
    test_evolution_comparison()
    test_api_import()
    
    print("✅ All tests passed!")
    print("🔄 Periodic analysis is now running in the background...")
    
    # Let it run for a few seconds to see the periodic analysis
    time.sleep(3)

if __name__ == "__main__":
    main()