import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

TOKENS_FILE = "tokens.json"
ANALYSIS_HISTORY_FILE = "analyses_history.json"

@app.get("/")
def root():
    print("Endpoint / appelé")
    return JSONResponse({"status": "ok", "message": "Tendy API is running."})

@app.post("/tokens")
async def save_tokens(request: Request):
    tokens = await request.json()
    print("Tokens reçus :", tokens)
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    print("tokens.json sauvegardé.")
    return JSONResponse({"status": "success", "message": "Tokens sauvegardés."})

@app.get("/tokens")
def get_tokens():
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        print("Tokens lus :", tokens)
    except FileNotFoundError:
        tokens = []
        print("Fichier tokens.json introuvable")
    return JSONResponse(tokens)

@app.get("/show_tokens")
def show_tokens():
    """
    Affiche le contenu brut de tokens.json (pour vérification Render).
    """
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print("Contenu brut de tokens.json :", content)
        return JSONResponse({"content": content})
    except FileNotFoundError:
        print("Fichier tokens.json introuvable (show_tokens)")
        return JSONResponse({"error": "Tokens file not found"}, status_code=404)

@app.post("/analyses_history")
async def save_analyses_history(request: Request):
    analyses = await request.json()
    print("Analyses reçues :", analyses)
    with open(ANALYSIS_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)
    print("analyses_history.json sauvegardé.")
    return JSONResponse({"status": "success", "message": "Analyses sauvegardées."})

@app.get("/analyses_history")
def get_analyses_history():
    try:
        with open(ANALYSIS_HISTORY_FILE, "r", encoding="utf-8") as f:
            analyses = json.load(f)
        print("Analyses lues :", analyses)
    except FileNotFoundError:
        analyses = {}
        print("Fichier analyses_history.json introuvable")
    return JSONResponse(analyses)

@app.get("/token_info")
def get_token_info(address: str):
    try:
        with open(TOKENS_FILE, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        print(f"Recherche du token {address} dans tokens.json")
    except FileNotFoundError:
        print("Fichier tokens.json introuvable (token_info)")
        return JSONResponse({"error": "Tokens file not found"}, status_code=404)
    for token in tokens:
        if token.get("token_address") == address:
            print("Token trouvé :", token)
            return JSONResponse(token)
    print("Token non trouvé :", address)
    return JSONResponse({"error": "Token not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
