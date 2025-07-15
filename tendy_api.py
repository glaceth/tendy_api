from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
TOKENS = []  # Stockage temporaire en mémoire

@app.post("/new_token")
async def receive_token(request: Request):
    token_data = await request.json()
    TOKENS.append(token_data)
    return JSONResponse({"status": "success", "received": token_data})

@app.get("/tokens")
def get_tokens():
    return TOKENS

if __name__ == "__main__":
    uvicorn.run("tendy_api:app", host="0.0.0.0", port=8000, reload=True)
