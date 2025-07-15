import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

TOKENS_FILE = "tokens.json"
ANALYSIS_HISTORY_FILE = "analyses_history.json"

@app.get("/")
def root():
    """Healthcheck simple"""
    return JSONResponse({"status": "ok", "message": "Tendy API is running."})

@app.post("/tokens")
async def save_tokens(request: Request):
    """
    Enregistre la liste des tokens envoyée par le PumpFun bot.
    """
    tokens = await request.json()
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    return JSONResponse({"status": "success", "message": "Tokens sauvegardés."})

@app.get("/tokens")
def get_tokens():
    """
    Récupère la liste des tokens pour le Tendy bot.
    """
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = []
    return JSONResponse(tokens)

@app.post("/analyses_history")
async def save_analyses_history(request: Request):
    """
    Enregistre l'historique des analyses envoyée par le PumpFun bot.
    """
    analyses = await request.json()
    with open(ANALYSIS_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)
    return JSONResponse({"status": "success", "message": "Analyses sauvegardées."})

@app.get("/analyses_history")
def get_analyses_history():
    """
    Récupère l'historique des analyses pour le Tendy bot.
    """
    try:
        with open(ANALYSIS_HISTORY_FILE, "r", encoding="utf-8") as f:
            analyses = json.load(f)
    except FileNotFoundError:
        analyses = {}
    return JSONResponse(analyses)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
