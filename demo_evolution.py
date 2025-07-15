#!/usr/bin/env python3
"""
Demonstration script showing Tendy API live data fetching and evolution tracking
"""

import json
import time
from datetime import datetime, timedelta

# Mock data to simulate live data changes
MOCK_TOKENS = [
    {
        "token_address": "0x1111111111111111111111111111111111111111",
        "name": "Moon Token",
        "symbol": "MOON",
        "mc": 1000000,
        "holders": 1000,
        "rugscore": 2.5,
        "honeypot": False,
        "lp_locked": True,
        "top_holders": ["0xabc123", "0xdef456"],
        "price_usd": 0.001,
        "timestamp": datetime.now().isoformat()
    },
    {
        "token_address": "0x2222222222222222222222222222222222222222",
        "name": "Safe Token",
        "symbol": "SAFE",
        "mc": 5000000,
        "holders": 2500,
        "rugscore": 1.0,
        "honeypot": False,
        "lp_locked": True,
        "top_holders": ["0x123abc", "0x456def", "0x789ghi"],
        "price_usd": 0.002,
        "timestamp": datetime.now().isoformat()
    }
]

def simulate_market_changes(token_data):
    """
    Simulate realistic market changes for demonstration
    """
    import random
    
    # Simulate market cap changes (-20% to +50%)
    mc_change = random.uniform(-0.2, 0.5)
    token_data["mc"] = int(token_data["mc"] * (1 + mc_change))
    
    # Simulate holder changes (-5% to +30%)
    holder_change = random.uniform(-0.05, 0.3)
    token_data["holders"] = int(token_data["holders"] * (1 + holder_change))
    
    # Simulate price changes (correlated with MC)
    price_change = mc_change * 0.8 + random.uniform(-0.1, 0.1)
    token_data["price_usd"] = token_data["price_usd"] * (1 + price_change)
    
    # Simulate rugscore changes (slight variations)
    rugscore_change = random.uniform(-0.5, 0.5)
    token_data["rugscore"] = max(0, min(10, token_data["rugscore"] + rugscore_change))
    
    # Update timestamp
    token_data["timestamp"] = datetime.now().isoformat()
    
    return token_data

def demonstrate_evolution_tracking():
    """
    Demonstrate the evolution tracking system
    """
    print("🚀 Tendy API Evolution Tracking Demo")
    print("=" * 50)
    
    # Import the analysis functions
    from analyze_with_gpt import format_evolution_data, analyze_token_with_gpt
    
    # Initialize with mock tokens
    with open("tokens.json", "w") as f:
        json.dump(MOCK_TOKENS, f, indent=2)
    
    print(f"📊 Initialized with {len(MOCK_TOKENS)} tokens")
    
    # Simulate 3 cycles of analysis
    history = {}
    
    for cycle in range(1, 4):
        print(f"\n🔄 Analysis Cycle {cycle}")
        print("-" * 30)
        
        # Load current tokens
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        
        for token in tokens:
            token_address = token["token_address"]
            print(f"\n📈 Analyzing {token['symbol']} ({token['name']})")
            
            # Simulate market changes for cycles 2 and 3
            if cycle > 1:
                # Get previous data for comparison
                previous_data = history[token_address][-1]["token_data"] if token_address in history else token
                
                # Simulate market changes
                updated_token = simulate_market_changes(token.copy())
                
                # Show evolution
                evolution = format_evolution_data(updated_token, previous_data)
                
                print("🔄 Evolution since last analysis:")
                for key, value in evolution.items():
                    print(f"  • {key}: {value}")
                
                # Create summary
                summary = (
                    f"Token: {updated_token['name']} ({updated_token['symbol']})\n"
                    f"Address: {token_address}\n"
                    f"Market Cap: ${updated_token['mc']:,}\n"
                    f"Price: ${updated_token['price_usd']:.6f}\n"
                    f"Holders: {updated_token['holders']:,}\n"
                    f"Rug Score: {updated_token['rugscore']:.1f}/10\n"
                    f"Honeypot: {'Yes' if updated_token['honeypot'] else 'No'}\n"
                    f"LP Locked: {'Yes' if updated_token['lp_locked'] else 'No'}\n"
                    f"Last Update: {updated_token['timestamp']}\n"
                )
                
                # Get analysis (will show API key warning without actual OpenAI key)
                analysis = analyze_token_with_gpt(summary, evolution)
                print(f"🧠 GPT Analysis Preview: {analysis[:100]}...")
                
                # Update token data
                tokens[tokens.index(token)] = updated_token
                
            else:
                # First cycle - just initialize
                evolution = {}
                analysis = f"Initial analysis for {token['symbol']}"
                updated_token = token
                print("🆕 First analysis - no evolution data yet")
            
            # Store in history
            if token_address not in history:
                history[token_address] = []
            
            history[token_address].append({
                "timestamp": updated_token["timestamp"],
                "token_data": updated_token,
                "analysis": analysis,
                "evolution": evolution
            })
        
        # Save updated tokens
        with open("tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
        
        # Save history
        with open("analyses_history.json", "w") as f:
            json.dump(history, f, indent=2)
        
        print(f"\n✅ Cycle {cycle} completed - data saved")
        
        # Wait before next cycle (shortened for demo)
        if cycle < 3:
            print("⏳ Waiting 2 seconds before next cycle...")
            time.sleep(2)
    
    print("\n🎉 Demo completed!")
    print("\nYou can now:")
    print("1. Start the API server: python -m uvicorn tendy_api:app --host 0.0.0.0 --port 8000")
    print("2. Check tokens: curl http://localhost:8000/tokens")
    print("3. Check history: curl http://localhost:8000/analyses/history")
    print("4. The periodic analysis will continue every 5 minutes")

if __name__ == "__main__":
    demonstrate_evolution_tracking()