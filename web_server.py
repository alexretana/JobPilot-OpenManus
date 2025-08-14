#!/usr/bin/env python3
"""
JobPilot-OpenManus Web Server
A simple FastAPI web interface for the JobPilot job hunting agent system.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from app.agent.manus import Manus
from app.logger import logger
from app.prompt.jobpilot import get_jobpilot_prompt


class ChatMessage(BaseModel):
    type: str  # "user" or "assistant" 
    content: str
    timestamp: datetime = datetime.now()


class JobSearchRequest(BaseModel):
    query: str
    experience_years: Optional[int] = None
    location: Optional[str] = None
    remote_only: bool = True


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


app = FastAPI(title="JobPilot-OpenManus", description="AI-Powered Job Hunting Assistant")
manager = ConnectionManager()

# Store chat history
chat_history: List[ChatMessage] = []

# Mount static files for the Solid.js frontend
import os
frontend_dist_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the Solid.js frontend index.html"""
        index_path = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return HTMLResponse(
                content="<h1>Frontend not built</h1><p>Please run 'npm run build' in the frontend directory.</p>",
                status_code=404
            )
else:
    @app.get("/")
    async def fallback_frontend():
        """Fallback when frontend is not built"""
        return HTMLResponse(
            content="<h1>Frontend not found</h1><p>Please build the frontend by running 'npm run build' in the frontend directory.</p>",
            status_code=404
        )


class ProgressStreamingAgent:
    """Agent wrapper that provides progress streaming to WebSocket clients."""
    
    def __init__(self, websocket: WebSocket, agent: Manus):
        self.websocket = websocket
        self.agent = agent
        self.current_step = 0
        self.total_steps = 20
        
    async def send_progress(self, message: str, step: int = None):
        """Send progress update to client."""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
            
        await self.websocket.send_text(json.dumps({
            "type": "progress",
            "content": message,
            "step": self.current_step,
            "total": self.total_steps,
            "timestamp": datetime.now().isoformat()
        }))
        
    async def send_tool_start(self, tool_name: str, args: dict = None):
        """Send tool start notification."""
        await self.websocket.send_text(json.dumps({
            "type": "tool_start",
            "tool": tool_name,
            "args": args,
            "timestamp": datetime.now().isoformat()
        }))
        
    async def send_tool_result(self, tool_name: str, result: str, url: str = None):
        """Send tool result notification."""
        await self.websocket.send_text(json.dumps({
            "type": "tool_result",
            "tool": tool_name,
            "content": result[:500] if result else None,  # Limit content size
            "url": url,
            "timestamp": datetime.now().isoformat()
        }))
        
    async def send_browser_action(self, action: str, url: str, content: str = None):
        """Send browser action notification."""
        await self.websocket.send_text(json.dumps({
            "type": "browser_action",
            "action": action,
            "url": url,
            "content": content[:200] if content else None,  # Limit content size
            "timestamp": datetime.now().isoformat()
        }))
        
    async def run_with_progress(self, user_message: str) -> str:
        """Run agent with progress streaming."""
        try:
            # Send initial progress
            await self.send_progress("🚀 JobPilot agent initializing...")
            
            # Inject JobPilot-specific system prompt
            import os
            current_dir = os.getcwd()
            jobpilot_prompt = get_jobpilot_prompt(current_dir)
            
            # Override the system prompt for this session
            original_prompt = getattr(self.agent, '_system_prompt', None)
            self.agent._system_prompt = jobpilot_prompt
            
            await self.send_progress("🎯 Analyzing your job search request...")
            
            # Create a custom step counter to track agent progress
            step_counter = {'value': 2}
            
            # Monkey patch the agent's tool execution to send progress
            original_execute_tool = None
            if hasattr(self.agent, 'execute_tool'):
                original_execute_tool = self.agent.execute_tool
                
                async def progress_execute_tool(tool_call):
                    tool_name = tool_call.function.name if hasattr(tool_call, 'function') else str(tool_call)
                    await self.send_progress(f"🔧 Using {tool_name} tool...", step_counter['value'])
                    await self.send_tool_start(tool_name)
                    
                    try:
                        result = await original_execute_tool(tool_call)
                        
                        # Extract URL and content from browser actions
                        url = None
                        content = None
                        if 'browser' in tool_name.lower() and result:
                            if 'http' in str(result):
                                import re
                                url_match = re.search(r'https?://[^\s]+', str(result))
                                if url_match:
                                    url = url_match.group()
                                    await self.send_browser_action('navigate', url, str(result))
                        
                        await self.send_tool_result(tool_name, str(result), url)
                        step_counter['value'] += 1
                        
                        return result
                    except Exception as e:
                        await self.send_progress(f"⚠️ Tool {tool_name} encountered an issue: {str(e)[:100]}...", step_counter['value'])
                        step_counter['value'] += 1
                        raise e
                
                self.agent.execute_tool = progress_execute_tool
            
            # Run the agent
            await self.send_progress("🔍 Starting job search process...", step_counter['value'])
            response = await self.agent.run(user_message)
            
            await self.send_progress("✅ Job search completed successfully!", self.total_steps)
            
            # Restore original methods
            if original_execute_tool:
                self.agent.execute_tool = original_execute_tool
            if original_prompt:
                self.agent._system_prompt = original_prompt
                
            return response
            
        except Exception as e:
            await self.send_progress(f"❌ Error during job search: {str(e)}", self.total_steps)
            raise e


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication with progress streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                # Add user message to history
                chat_history.append(ChatMessage(type="user", content=user_message))
                
                # Process with JobPilot agent with progress streaming
                try:
                    # Create agent
                    agent = await Manus.create()
                    
                    # Create progress streaming wrapper
                    progress_agent = ProgressStreamingAgent(websocket, agent)
                    
                    # Run with progress updates
                    response = await progress_agent.run_with_progress(user_message)
                    
                    # Add assistant response to history
                    chat_history.append(ChatMessage(type="assistant", content=response))
                    
                    # Send final response back to client
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "response",
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    
                    await agent.cleanup()
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error", 
                            "content": error_msg,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    logger.error(f"Agent error: {e}")
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "JobPilot-OpenManus", "timestamp": datetime.now()}


@app.get("/api/chat/history")
async def get_chat_history():
    """Get chat history."""
    return {"messages": chat_history}


@app.get("/api/jobs/recent")
async def get_recent_jobs(limit: int = 20):
    """Get recently posted jobs."""
    try:
        from app.data.database import get_job_repository
        job_repo = get_job_repository()
        jobs = job_repo.get_recent_jobs(limit=min(limit, 50))
        
        return {
            "jobs": [
                {
                    "id": str(job.id),
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type.value if job.job_type else None,
                    "remote_type": job.remote_type.value if job.remote_type else None,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_currency": job.salary_currency,
                    "skills_required": job.skills_required[:5] if job.skills_required else [],
                    "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                    "description": job.description[:200] + "..." if job.description and len(job.description) > 200 else job.description,
                    "job_url": job.job_url
                }
                for job in jobs
            ],
            "total": len(jobs),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information for a specific job."""
    try:
        from app.data.database import get_job_repository
        job_repo = get_job_repository()
        job = job_repo.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type.value if job.job_type else None,
            "remote_type": job.remote_type.value if job.remote_type else None,
            "experience_level": job.experience_level.value if job.experience_level else None,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "description": job.description,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "skills_required": job.skills_required,
            "skills_preferred": job.skills_preferred,
            "benefits": job.benefits,
            "company_size": job.company_size,
            "industry": job.industry,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "job_url": job.job_url,
            "source": job.source,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/search")
async def search_jobs_simple(query: str = "", job_types: str = "", locations: str = "", limit: int = 20):
    """Search jobs using filters (simple version for direct API calls)."""
    try:
        from app.data.database import get_job_repository
        from app.data.models import JobType
        job_repo = get_job_repository()
        
        # Parse job types
        parsed_job_types = None
        if job_types:
            parsed_job_types = []
            for jt in job_types.split(","):
                try:
                    parsed_job_types.append(JobType(jt.strip()))
                except ValueError:
                    pass  # Skip invalid job types
        
        # Parse locations
        location_list = [loc.strip() for loc in locations.split(",") if loc.strip()] if locations else None
        
        jobs, total = job_repo.search_jobs(
            query=query or None,
            job_types=parsed_job_types,
            locations=location_list,
            limit=min(limit, 50)
        )
        
        return {
            "jobs": [
                {
                    "id": str(job.id),
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type.value if job.job_type else None,
                    "remote_type": job.remote_type.value if job.remote_type else None,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "skills_required": job.skills_required[:5] if job.skills_required else [],
                    "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                    "description": job.description[:200] + "..." if job.description and len(job.description) > 200 else job.description,
                }
                for job in jobs
            ],
            "total": total,
            "query": query,
            "filters": {
                "job_types": job_types,
                "locations": locations
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/search/agent")
async def search_jobs_agent(request: JobSearchRequest):
    """Search for jobs using the JobPilot agent (original functionality)."""
    try:
        agent = await Manus.create()
        
        # Build query from request
        query_parts = [request.query]
        if request.experience_years:
            query_parts.append(f"with {request.experience_years} years of experience")
        if request.location:
            query_parts.append(f"in {request.location}")
        if request.remote_only:
            query_parts.append("remote work preferred")
            
        full_query = " ".join(query_parts)
        
        response = await agent.run(full_query)
        await agent.cleanup()
        
        return {"query": full_query, "response": response, "timestamp": datetime.now()}
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


                

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JobPilot-OpenManus Web Server")
    parser.add_argument(
        "--host", 
        default="localhost", 
        help="Host to bind the server to (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080, 
        help="Port to bind the server to (default: 8080)"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting JobPilot-OpenManus Web Server")
    logger.info("📦 Serving built frontend from dist/ directory")
    
    try:
        logger.info(f"Starting JobPilot-OpenManus Web Server on {args.host}:{args.port}...")
        uvicorn.run(
            "web_server:app",
            host=args.host,
            port=args.port,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
