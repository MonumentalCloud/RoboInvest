from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from backend.api.governor_endpoints import router as governor_router

app = FastAPI(title="RoboInvest API", version="1.0.0")

# Include only the governor router
app.include_router(governor_router, prefix="/api/governor")

# Health check endpoint for startup script
@app.get("/api/health")
async def health_check():
    """Health check endpoint for startup script"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 