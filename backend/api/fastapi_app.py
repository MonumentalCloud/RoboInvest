from __future__ import annotations

import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Add backend directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api.governor_endpoints import router as governor_router
from api.reasoning_endpoints import router as reasoning_router

app = FastAPI(title="RoboInvest API", version="1.0.0")

# Include routers
app.include_router(governor_router)
app.include_router(reasoning_router)

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