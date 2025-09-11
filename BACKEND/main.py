from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
import json
import os
from datetime import datetime
import uuid

# Import our custom modules
from chatbot_engine import ChatbotEngine
from language_processor import LanguageProcessor
from conversation_logger import ConversationLogger

app = FastAPI(title="Multilingual Campus Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
chatbot_engine = ChatbotEngine()
language_processor = LanguageProcessor()
conversation_logger = ConversationLogger()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    detected_language: str
    session_id: str
    confidence: float
    needs_human: bool = False
    suggested_contact: Optional[str] = None

class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    message_count: int
    languages_used: List[str]

# Routes
@app.get("/")
async def root():
    return {
        "message": "Multilingual Campus Chatbot API",
        "version": "1.0.0",
        "supported_languages": ["en", "hi", "gu", "mr", "raj"],
        "endpoints": ["/chat", "/health", "/sessions", "/logs"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Main chat endpoint - processes user messages and returns responses"""
    try:
        # Generate session ID if not provided
        if not message.session_id:
            message.session_id = str(uuid.uuid4())
        
        # Detect language if not specified
        if not message.language:
            detected_lang = language_processor.detect_language(message.message)
        else:
            detected_lang = message.language
        
        # Process message through chatbot engine
        response_data = await chatbot_engine.process_message(
            message.message, 
            message.session_id, 
            detected_lang
        )
        
        # Log the conversation
        await conversation_logger.log_conversation(
            session_id=message.session_id,
            user_message=message.message,
            bot_response=response_data["response"],
            language=detected_lang,
            confidence=response_data["confidence"]
        )
        
        return ChatResponse(
            response=response_data["response"],
            detected_language=detected_lang,
            session_id=message.session_id,
            confidence=response_data["confidence"],
            needs_human=response_data.get("needs_human", False),
            suggested_contact=response_data.get("contact", None)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "chatbot_engine": "ok",
            "language_processor": "ok",
            "conversation_logger": "ok"
        }
    }

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    try:
        session_info = await conversation_logger.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        return session_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/daily")
async def get_daily_logs(date: Optional[str] = None):
    """Get daily conversation logs for analysis"""
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logs = await conversation_logger.get_daily_logs(date)
        return {
            "date": date,
            "total_conversations": len(logs),
            "languages_used": list(set([log["language"] for log in logs])),
            "conversations": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/widget/embed.js")
async def get_embed_script():
    """Return the embeddable widget JavaScript"""
    embed_script = """
    (function() {
        // Create chat widget iframe
        const iframe = document.createElement('iframe');
        iframe.src = window.location.origin + '/widget/chat.html';
        iframe.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            border: none;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            z-index: 10000;
            background: white;
        `;
        
        // Add toggle button
        const button = document.createElement('button');
        button.innerHTML = '💬';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: none;
            background: #007bff;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            z-index: 10001;
        `;
        
        let isOpen = false;
        iframe.style.display = 'none';
        
        button.onclick = function() {
            isOpen = !isOpen;
            iframe.style.display = isOpen ? 'block' : 'none';
            button.innerHTML = isOpen ? '✕' : '💬';
        };
        
        document.body.appendChild(iframe);
        document.body.appendChild(button);
    })();
    """
    return embed_script

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
