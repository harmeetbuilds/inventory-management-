from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import forecast, inventory

app = FastAPI(title="Inventory Management AI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["Forecast"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])

@app.get("/")
def root():
    return {"status": "Online", "service": "Inventory Management ML Backend"}