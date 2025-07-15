from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import requests

from analyze_with_gpt import analyze_token_with_gpt  # Assure-toi que le chemin d'import est correct

app = FastAPI()
TOKENS = []  # Stockage temporaire en mémoire

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")      # Ton token Telegram Tendy
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Ton chat Tendy

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)

def make_summary(token_data):
    return (
        f"Nom: {token_data.get('name')}\n"
        f"Ticker: {token_data.get('symbol')}\n"
        f"Market Cap: {token_data.get('mc')}\n"
        f"Holders: {token_data.get('holders')}\n"
        f"Rugscore: {token_data.get('rugscore')}\n"
        f"Honeypot: {token_data.get('honeypot')}\n"
        f"LP Locked: {token_data.get('lp_locked')}\n"
        f"Top Holders: {token_data.get('top_holders')}\n"
        f"Timestamp: {token_data.get('timestamp')}\n"
    )

@app.post("/new_token")
async def receive_token(request: Request):
    token_data = await request.json()
    TOKENS.append(token_data)
    summary = make_summary(token_data)
    analysis = analyze_token_with_gpt(summary)
    message = f"🧠 Analyse GPT pour {token_data.get('symbol', '?')} ({token_data.get('token_address')}):\n{analysis}"
    send_telegram_message(message)
    return JSONResponse({"status": "success", "received": token_data, "gpt_analysis": analysis})

@app.get("/tokens")
def get_tokens():
    return TOKENS

if __name__ == "__main__":
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
