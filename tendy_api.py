import os
import requests
import time
import threading
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from analyze_with_gpt import analyze_token_with_gpt, format_evolution_data

app = FastAPI()
TOKENS_FILE = "tokens.json"
ANALYSES_HISTORY_FILE = "analyses_history.json"

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tokens(tokens):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def load_analyses_history():
    """Load historical analyses data"""
    if os.path.exists(ANALYSES_HISTORY_FILE):
        with open(ANALYSES_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_analyses_history(history):
    """Save historical analyses data"""
    with open(ANALYSES_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_live_data_moralis(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch live data from Moralis API
    """
    try:
        moralis_api_key = os.getenv('MORALIS_API_KEY')
        if not moralis_api_key:
            print("⚠️ MORALIS_API_KEY not configured")
            return None
        
        headers = {
            'X-API-Key': moralis_api_key,
            'accept': 'application/json'
        }
        
        # Get token metadata
        metadata_url = f"https://deep-index.moralis.io/api/v2/erc20/{token_address}/metadata"
        metadata_response = requests.get(metadata_url, headers=headers, timeout=10)
        
        if metadata_response.status_code != 200:
            print(f"⚠️ Moralis metadata API error: {metadata_response.status_code}")
            return None
        
        metadata = metadata_response.json()
        
        # Get token price (if available)
        price_url = f"https://deep-index.moralis.io/api/v2/erc20/{token_address}/price"
        price_response = requests.get(price_url, headers=headers, timeout=10)
        
        price_data = {}
        if price_response.status_code == 200:
            price_data = price_response.json()
        
        return {
            'name': metadata.get('name', 'Unknown'),
            'symbol': metadata.get('symbol', 'Unknown'),
            'decimals': metadata.get('decimals', 18),
            'price_usd': price_data.get('usdPrice', 0),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching Moralis data: {str(e)}")
        return None

def get_live_data_rugcheck(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch live data from RugCheck API
    """
    try:
        rugcheck_url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
        
        headers = {
            'User-Agent': 'TendyAPI/1.0'
        }
        
        response = requests.get(rugcheck_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ RugCheck API error: {response.status_code}")
            return None
        
        data = response.json()
        
        return {
            'rugscore': data.get('score', 0),
            'honeypot': data.get('risks', {}).get('honeypot', False),
            'lp_locked': data.get('risks', {}).get('liquidityLocked', False),
            'top_holders': data.get('topHolders', []),
            'holders': data.get('holderCount', 0),
            'mc': data.get('marketCap', 0),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching RugCheck data: {str(e)}")
        return None

def merge_live_data(moralis_data: Optional[Dict], rugcheck_data: Optional[Dict], original_data: Dict) -> Dict:
    """
    Merge live data from different sources with original token data
    """
    merged = original_data.copy()
    
    # Update with Moralis data
    if moralis_data:
        merged.update(moralis_data)
    
    # Update with RugCheck data
    if rugcheck_data:
        merged.update(rugcheck_data)
    
    # Always update timestamp
    merged['timestamp'] = datetime.now().isoformat()
    
    return merged

@app.post("/new_token")
async def receive_token(request: Request):
    token_data = await request.json()
    tokens = load_tokens()
    # Ajout sans doublon
    if not any(t.get('token_address') == token_data.get('token_address') for t in tokens):
        tokens.append(token_data)
        save_tokens(tokens)
    return JSONResponse({"status": "success", "received": token_data})

@app.get("/tokens")
def get_tokens():
    return load_tokens()

@app.get("/analyses/history")
def get_analyses_history():
    """Get historical analyses for all tokens"""
    return load_analyses_history()

@app.get("/analyses/history/{token_address}")
def get_token_analyses_history(token_address: str):
    """Get historical analyses for a specific token"""
    history = load_analyses_history()
    return history.get(token_address, [])

# Tâche périodique d'analyse
def periodic_analysis():
    while True:
        try:
            print(f"🔄 Starting periodic analysis at {datetime.now().isoformat()}")
            
            tokens = load_tokens()
            history = load_analyses_history()
            
            for token in tokens:
                try:
                    token_address = token.get('token_address')
                    if not token_address:
                        print(f"⚠️ Token missing address: {token}")
                        continue
                    
                    print(f"📊 Analyzing token: {token.get('symbol', 'Unknown')} ({token_address})")
                    
                    # Get live data from external APIs
                    moralis_data = get_live_data_moralis(token_address)
                    rugcheck_data = get_live_data_rugcheck(token_address)
                    
                    # Merge all data
                    updated_token = merge_live_data(moralis_data, rugcheck_data, token)
                    
                    # Get previous analysis for comparison
                    token_history = history.get(token_address, [])
                    previous_data = token_history[-1] if token_history else None
                    
                    # Format evolution data for GPT
                    evolution_data = None
                    if previous_data:
                        evolution_data = format_evolution_data(updated_token, previous_data)
                    
                    # Create summary for GPT
                    summary = (
                        f"Token: {updated_token.get('name', 'Unknown')} ({updated_token.get('symbol', 'Unknown')})\n"
                        f"Address: {token_address}\n"
                        f"Market Cap: ${updated_token.get('mc', 0):,}\n"
                        f"Price: ${updated_token.get('price_usd', 0):.6f}\n"
                        f"Holders: {updated_token.get('holders', 0):,}\n"
                        f"Rug Score: {updated_token.get('rugscore', 0)}/10\n"
                        f"Honeypot: {'Yes' if updated_token.get('honeypot', False) else 'No'}\n"
                        f"LP Locked: {'Yes' if updated_token.get('lp_locked', False) else 'No'}\n"
                        f"Top Holders: {len(updated_token.get('top_holders', []))} tracked\n"
                        f"Last Update: {updated_token.get('timestamp', 'Unknown')}\n"
                    )
                    
                    # Get GPT analysis
                    analysis = analyze_token_with_gpt(summary, evolution_data)
                    
                    # Store analysis in history
                    analysis_entry = {
                        'timestamp': updated_token.get('timestamp'),
                        'token_data': updated_token,
                        'analysis': analysis,
                        'evolution': evolution_data or {}
                    }
                    
                    if token_address not in history:
                        history[token_address] = []
                    
                    history[token_address].append(analysis_entry)
                    
                    # Keep only last 100 entries per token to avoid file bloat
                    if len(history[token_address]) > 100:
                        history[token_address] = history[token_address][-100:]
                    
                    # Update token in tokens list
                    for i, t in enumerate(tokens):
                        if t.get('token_address') == token_address:
                            tokens[i] = updated_token
                            break
                    
                    print(f"✅ Analysis completed for {updated_token.get('symbol', 'Unknown')}")
                    
                    # Here you would send to Telegram
                    # send_telegram_message(f"🧠 GPT Analysis for {updated_token.get('symbol')}:\n{analysis}")
                    
                except Exception as e:
                    print(f"⚠️ Error analyzing token {token.get('symbol', 'Unknown')}: {str(e)}")
                    continue
            
            # Save updated data
            save_tokens(tokens)
            save_analyses_history(history)
            
            print(f"✅ Periodic analysis completed at {datetime.now().isoformat()}")
            
        except Exception as e:
            print(f"⚠️ Error in periodic analysis: {str(e)}")
        
        time.sleep(300)  # 5 minutes

# Démarrage de la tâche périodique
threading.Thread(target=periodic_analysis, daemon=True).start()
