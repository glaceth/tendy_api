import os
import requests
import time
import threading
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from analyze_with_gpt import analyze_token_with_gpt

app = FastAPI()
TOKENS_FILE = "tokens.json"
ANALYSIS_HISTORY_FILE = "analyses_history.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MORALIS_API_KEY = os.getenv("MORALIS_API_KEY")

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tokens(tokens):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def load_analysis_history():
    if os.path.exists(ANALYSIS_HISTORY_FILE):
        with open(ANALYSIS_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_analysis_history(history):
    with open(ANALYSIS_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)

def get_moralis_data(token_address):
    url = "https://solana-gateway.moralis.io/token/mainnet/exchange/pumpfun/graduated?limit=100"
    headers = {"Accept": "application/json", "X-API-Key": MORALIS_API_KEY}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json().get("result", [])
        for token in data:
            if token.get("tokenAddress") == token_address:
                return {
                    "mc": token.get("fullyDilutedValuation"),
                    "holders": token.get("holders"),
                    "liquidity": token.get("liquidity"),
                    "name": token.get("name"),
                    "symbol": token.get("symbol"),
                }
        return None
    except Exception as e:
        print(f"Moralis error: {e}")
        return None

def get_rugcheck_data(token_address):
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "rugscore": data.get("score_normalised") or data.get("score"),
                "honeypot": any("honeypot" in r.get("name", "").lower() for r in data.get("risks", [])),
                "lp_locked": any(
                    market.get("lp", {}).get("lpLockedPct", 0) >= 75 and market.get("lp", {}).get("lpLockedUSD", 0) > 2500
                    for market in data.get("markets", [])
                ),
            }
        else:
            print(f"RugCheck error: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"RugCheck error: {e}")
        return None

def make_summary(token, prev_analysis=None, live_data=None):
    lines = []
    lines.append(f"Nom : {token.get('name')}")
    lines.append(f"Ticker : {token.get('symbol')}")
    lines.append(f"Market Cap : {live_data.get('mc') if live_data else token.get('mc')}")
    lines.append(f"Holders : {live_data.get('holders') if live_data else token.get('holders')}")
    lines.append(f"Rugscore : {live_data.get('rugscore') if live_data else token.get('rugscore')}")
    lines.append(f"Honeypot : {live_data.get('honeypot') if live_data else token.get('honeypot')}")
    lines.append(f"LP Locked : {live_data.get('lp_locked') if live_data else token.get('lp_locked')}")
    lines.append(f"Top Holders : {token.get('top_holders')}")

    # Ajout comparatif
    if prev_analysis and live_data:
        try:
            mc_before = float(prev_analysis.get("mc", 0))
            mc_now = float(live_data.get("mc", 0))
            holders_before = int(prev_analysis.get("holders", 0))
            holders_now = int(live_data.get("holders", 0))
            if mc_before and mc_now:
                delta_mc = mc_now - mc_before
                pct_mc = (delta_mc / mc_before) * 100 if mc_before else 0
                lines.append(f"→ MC évolue : {mc_before} → {mc_now} USD ({pct_mc:+.2f}%)")
            if holders_before and holders_now:
                delta_holders = holders_now - holders_before
                pct_holders = (delta_holders / holders_before) * 100 if holders_before else 0
                lines.append(f"→ Holders évoluent : {holders_before} → {holders_now} ({pct_holders:+.2f}%)")
        except Exception as e:
            lines.append("Erreur comparaison évolution.")
    return "\n".join(lines)

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

# Tâche périodique d'analyse
def periodic_analysis():
    while True:
        tokens = load_tokens()
        history = load_analysis_history()
        for token in tokens:
            token_address = token.get("token_address")
            live_moralis = get_moralis_data(token_address)
            live_rugcheck = get_rugcheck_data(token_address)
            if live_moralis and live_rugcheck:
                live_data = {**live_moralis, **live_rugcheck}
            else:
                live_data = None

            prev_analyses = history.get(token_address, [])
            prev_analysis = prev_analyses[-1] if prev_analyses else None

            summary = make_summary(token, prev_analysis, live_data)
            gpt_result = analyze_token_with_gpt(summary)

            # Enregistre dans l'historique
            analysis_entry = {
                "timestamp": int(time.time()),
                "mc": live_data.get("mc") if live_data else token.get("mc"),
                "holders": live_data.get("holders") if live_data else token.get("holders"),
                "rugscore": live_data.get("rugscore") if live_data else token.get("rugscore"),
                "honeypot": live_data.get("honeypot") if live_data else token.get("honeypot"),
                "lp_locked": live_data.get("lp_locked") if live_data else token.get("lp_locked"),
                "gpt": gpt_result
            }
            if token_address not in history:
                history[token_address] = []
            history[token_address].append(analysis_entry)
            save_analysis_history(history)

            # Envoie sur Telegram
            message = f"🧠 Analyse évolutive PumpFun\nToken : {token.get('symbol')} ({token_address})\n\n{gpt_result}"
            send_telegram_message(message)
        time.sleep(300)  # 5 min

threading.Thread(target=periodic_analysis, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
