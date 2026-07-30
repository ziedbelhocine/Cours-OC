# main.py
from fastapi import FastAPI
from routers import items  # On importe notre module de routes

app = FastAPI(title="Mon API bien structurée")

# On attache le routeur d'items à l'application principale
app.include_router(items.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API !"}