#!/usr/bin/env python3
"""
JobPilot-OpenManus Web Server
A simple FastAPI web interface for the JobPilot job hunting agent system.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from app.agent.manus import Manus
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


@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Return the main web interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JobPilot-OpenManus - AI Job Hunting Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header h1 {
                color: #4a5568;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .header .subtitle {
                color: #718096;
                font-size: 0.9rem;
                margin-top: 0.25rem;
            }
            .main-container {
                flex: 1;
                display: flex;
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
                gap: 2rem;
                width: 100%;
            }
            .chat-container {
                flex: 2;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                min-height: 500px;
            }
            .chat-header {
                background: #4299e1;
                color: white;
                padding: 1rem;
                border-radius: 12px 12px 0 0;
                font-weight: bold;
            }
            .chat-messages {
                flex: 1;
                padding: 1rem;
                overflow-y: auto;
                max-height: 400px;
            }
            .message {
                margin-bottom: 1rem;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                max-width: 80%;
            }
            .user-message {
                background: #e2e8f0;
                margin-left: auto;
                text-align: right;
            }
            .assistant-message {
                background: #f7fafc;
                border-left: 4px solid #4299e1;
            }
            .input-area {
                padding: 1rem;
                border-top: 1px solid #e2e8f0;
                display: flex;
                gap: 0.5rem;
            }
            .input-area input {
                flex: 1;
                padding: 0.75rem;
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                font-size: 1rem;
            }
            .input-area button {
                background: #4299e1;
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
            }
            .input-area button:hover {
                background: #3182ce;
            }
            .sidebar {
                flex: 1;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                padding: 1.5rem;
            }
            .sidebar h3 {
                color: #4a5568;
                margin-bottom: 1rem;
                font-size: 1.1rem;
            }
            .quick-actions {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .quick-action {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                padding: 0.75rem;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                font-size: 0.9rem;
            }
            .quick-action:hover {
                background: #edf2f7;
                border-color: #cbd5e0;
            }
            .status {
                margin-top: 1rem;
                padding: 0.75rem;
                background: #f0fff4;
                border: 1px solid #9ae6b4;
                border-radius: 6px;
                font-size: 0.9rem;
            }
            .loading {
                display: none;
                color: #718096;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 JobPilot-OpenManus</h1>
            <div class="subtitle">AI-Powered Job Hunting Assistant with Local Ollama Integration</div>
        </div>
        
        <div class="main-container">
            <div class="chat-container">
                <div class="chat-header">
                    💬 Chat with JobPilot Agent
                </div>
                <div class="chat-messages" id="messages">
                    <div class="message assistant-message">
                        👋 Hello! I'm your JobPilot AI assistant. I can help you find job opportunities, analyze market trends, and optimize your applications. 
                        <br><br>
                        Try asking me something like: "Show me Python developer jobs with 5 years experience in data science"
                    </div>
                </div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Ask about job opportunities..." />
                    <button onclick="sendMessage()">Send</button>
                </div>
                <div class="loading" id="loading">🤖 JobPilot is thinking...</div>
            </div>
            
            <div class="sidebar">
                <h3>🎯 Quick Actions</h3>
                <div class="quick-actions">
                    <button class="quick-action" onclick="quickQuery('Show me remote Python developer jobs')">
                        🐍 Find Python Jobs
                    </button>
                    <button class="quick-action" onclick="quickQuery('Data science jobs for 5 years experience')">
                        📊 Data Science Positions  
                    </button>
                    <button class="quick-action" onclick="quickQuery('Help me optimize my resume for tech roles')">
                        📄 Resume Optimization
                    </button>
                    <button class="quick-action" onclick="quickQuery('What are the current trends in AI/ML job market?')">
                        📈 Market Analysis
                    </button>
                    <button class="quick-action" onclick="quickQuery('Generate a cover letter template for software engineering')">
                        ✍️ Cover Letter Help
                    </button>
                </div>
                
                <div class="status">
                    <strong>🟢 Status:</strong> Connected to Ollama<br>
                    <strong>🧠 Model:</strong> gpt-oss:20b<br>
                    <strong>🔧 Tools:</strong> Job Search, Browser, Analysis
                </div>
            </div>
        </div>

        <script>
            const ws = new WebSocket('ws://localhost:8080/ws');
            const messages = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const loading = document.getElementById('loading');

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.content, 'assistant');
                hideLoading();
            };

            function addMessage(content, type) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }

            function showLoading() {
                loading.style.display = 'block';
            }

            function hideLoading() {
                loading.style.display = 'none';
            }

            function sendMessage() {
                const message = messageInput.value.trim();
                if (message) {
                    addMessage(message, 'user');
                    showLoading();
                    ws.send(JSON.stringify({type: 'message', content: message}));
                    messageInput.value = '';
                }
            }

            function quickQuery(query) {
                messageInput.value = query;
                sendMessage();
            }

            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                # Add user message to history
                chat_history.append(ChatMessage(type="user", content=user_message))
                
                # Process with JobPilot agent
                try:
                    agent = await Manus.create()
                    
                    # Run the agent with user query
                    response = await agent.run(user_message)
                    
                    # Add assistant response to history
                    chat_history.append(ChatMessage(type="assistant", content=response))
                    
                    # Send response back to client
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


@app.post("/api/jobs/search")
async def search_jobs(request: JobSearchRequest):
    """Search for jobs using the JobPilot agent."""
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
    logger.info("Starting JobPilot-OpenManus Web Server...")
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
