import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

DATA_FILE = "pumpfun_data.json"

@app.get("/")
def root():
    """Healthcheck simple"""
    return JSONResponse({"status": "ok", "message": "Tendy API is running."})

@app.post("/transfer")
async def transfer_data(request: Request):
    """
    Reçoit les infos du PumpFun Bot (POST) et les sauvegarde pour le Tendy Bot.
    """
    data = await request.json()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return JSONResponse({"status": "success", "message": "Data transférée."})

@app.get("/data")
def get_data():
    """
    Permet au Tendy Bot de récupérer les infos envoyées par le PumpFun Bot.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return JSONResponse(data)

# Optionnel : endpoint pour effacer les données
@app.post("/reset")
def reset_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        return JSONResponse({"status": "reset", "message": "Data effacée."})
    return JSONResponse({"status": "reset", "message": "Aucune data à effacer."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
