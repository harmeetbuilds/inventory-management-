from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import forecast, inventory
import os

app = FastAPI(title="Inventory Management AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount backend API routers
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["Forecast"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
# In backend/main.py
app.include_router(forecast.router, prefix="/api/v1/forecast")

# Serve Frontend Dashboard
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/dashboard")
def get_dashboard():
    return FileResponse("frontend/index.html")

@app.get("/")
def root():
    return {"status": "Online", "service": "Inventory Management ML Backend", "dashboard": "/dashboard"}