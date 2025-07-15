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

@app.get("/show_tokens")
def show_tokens():
    """
    Affiche le contenu brut de tokens.json (pour vérification Render).
    """
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return JSONResponse(content)
    except FileNotFoundError:
        return JSONResponse({"error": "Tokens file not found"}, status_code=404)

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

@app.get("/token_info")
def get_token_info(address: str):
    """
    Récupère les infos d'un token précis (par son address).
    """
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        return JSONResponse({"error": "Tokens file not found"}, status_code=404)

    for token in tokens:
        if token.get("token_address") == address:
            return JSONResponse(token)
    return JSONResponse({"error": "Token not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
