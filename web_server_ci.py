#!/usr/bin/env python3
"""
CI-Friendly JobPilot-OpenManus Web Server
A minimal FastAPI web server for CI testing without browser dependencies.
"""

from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.applications_simple import router as applications_router
from app.api.enhanced_jobs_api import router as enhanced_jobs_router
from app.api.leads_simple import router as leads_router
from app.api.timeline import router as timeline_router
from app.api.user_profiles import router as user_profiles_router
from app.logger import logger


class ChatMessage(BaseModel):
    type: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()


class JobSearchRequest(BaseModel):
    query: str
    experience_years: Optional[int] = None
    location: Optional[str] = None
    remote_only: bool = True


class SaveJobRequest(BaseModel):
    job_id: str
    notes: Optional[str] = None
    tags: List[str] = []


app = FastAPI(
    title="JobPilot-OpenManus CI", description="CI-Friendly Job Hunting Assistant API"
)

# Include API routers
app.include_router(timeline_router)
app.include_router(applications_router)
app.include_router(leads_router)
app.include_router(enhanced_jobs_router)
app.include_router(user_profiles_router)

# Store chat history
chat_history: List[ChatMessage] = []


@app.get("/")
async def root():
    """Root endpoint for health checks"""
    return JSONResponse(
        content={
            "message": "JobPilot-OpenManus CI Server",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "ci-test",
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "server": "jobpilot-ci",
            "timestamp": datetime.now().isoformat(),
            "user_profiles": "enabled",
            "database": "sqlite",
        }
    )


@app.get("/api/status")
async def api_status():
    """API status check"""
    return JSONResponse(
        content={
            "apis": {
                "user_profiles": "available",
                "timeline": "available",
                "applications": "available",
                "leads": "available",
                "enhanced_jobs": "available",
            },
            "database": "connected",
            "test_mode": True,
        }
    )


if __name__ == "__main__":
    logger.info("Starting JobPilot-OpenManus CI Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
