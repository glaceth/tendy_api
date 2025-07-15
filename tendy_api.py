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

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tokens(tokens):
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

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
        for token in tokens:
            # Ici tu peux re-fetch les données live via Moralis/RugCheck...
            # Par exemple:
            # updated_data = get_latest_data(token["token_address"])
            # token.update(updated_data)
            summary = (
                f"Nom: {token.get('name')}\n"
                f"Ticker: {token.get('symbol')}\n"
                f"Market Cap: {token.get('mc')}\n"
                f"Holders: {token.get('holders')}\n"
                f"Rugscore: {token.get('rugscore')}\n"
                f"Honeypot: {token.get('honeypot')}\n"
                f"LP Locked: {token.get('lp_locked')}\n"
                f"Top Holders: {token.get('top_holders')}\n"
                f"Timestamp: {token.get('timestamp')}\n"
            )
            analysis = analyze_token_with_gpt(summary)
            # Envoie sur Telegram ou stocke l'analyse
            # send_telegram_message(f"🧠 Update GPT pour {token.get('symbol')}:\n{analysis}")
        time.sleep(300)  # 5 minutes

# Démarrage de la tâche périodique
threading.Thread(target=periodic_analysis, daemon=True).start()
