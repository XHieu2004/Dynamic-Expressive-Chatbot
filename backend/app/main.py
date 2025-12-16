from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import json

from app.services.gemini_service import gemini_service
from app.services.emotion_manager import emotion_manager
from app.services.history_manager import history_manager
from app.services.image_generator import image_generator
from app.core.config import settings
from app.core.database import engine, get_db, Base
from app import models

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
os.makedirs(settings.STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(session_id)

async def generate_and_notify(session_id: str, emotion_description: str):
    # Generate Image
    image_url = await image_generator.generate_avatar(emotion_description)
    
    if image_url:
        # Update ChromaDB
        emotion_id = f"generated_{uuid.uuid4()}"
        emotion_manager.add_emotion(
            emotion_id=emotion_id,
            description=emotion_description,
            image_path=image_url,
            source="ai-generated"
        )
        
        # Notify Frontend
        await manager.send_personal_message({
            "event": "avatar_update",
            "avatar_url": f"http://localhost:8000{image_url}"
        }, session_id)

# --- Pydantic Models ---
class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    sender: str
    content: str
    timestamp: str

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    user_message: str
    session_id: str

# --- Session Endpoints ---

@app.post("/api/v1/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    session_id = f"session_{uuid.uuid4()}"
    db_session = models.ChatSession(id=session_id, title=session.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return SessionResponse(
        id=db_session.id, 
        title=db_session.title, 
        created_at=db_session.created_at.isoformat()
    )

@app.get("/api/v1/sessions", response_model=List[SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.ChatSession).order_by(models.ChatSession.created_at.desc()).all()
    return [
        SessionResponse(
            id=s.id, 
            title=s.title, 
            created_at=s.created_at.isoformat()
        ) for s in sessions
    ]

@app.get("/api/v1/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.timestamp).all()
    return [
        MessageResponse(
            sender=m.sender, 
            content=m.content, 
            timestamp=m.timestamp.isoformat()
        ) for m in messages
    ]

@app.delete("/api/v1/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "success", "message": "Session deleted"}

@app.post("/api/v1/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Ensure session exists in SQLite
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == request.session_id).first()
    if not db_session:
        # Auto-create if not exists (fallback)
        db_session = models.ChatSession(id=request.session_id, title="New Chat")
        db.add(db_session)
        db.commit()

    # Save User Message to SQLite
    user_msg = models.ChatMessage(session_id=request.session_id, sender="user", content=request.user_message)
    db.add(user_msg)
    db.commit()

    # Phase 3: Automated Generation & Real-time Experience
    
    # 0. Retrieve Context (History)
    context = history_manager.retrieve_context(request.session_id, request.user_message)
    if not context:
        context = history_manager.retrieve_last_n(request.session_id)

    # 1. Get text response and emotion description from Gemini
    gemini_response = await gemini_service.generate_response(request.user_message, context)
    reply_text = gemini_response.get("reply_text", "")
    emotion_description = gemini_response.get("emotion_description", "neutral")
    emotion_category = gemini_response.get("emotion_category", "neutral").lower()
    
    # Save Bot Message to SQLite
    bot_msg = models.ChatMessage(session_id=request.session_id, sender="bot", content=reply_text)
    db.add(bot_msg)
    db.commit()

    # Update Session Title if it's the first message
    if db_session.title == "New Chat":
        # Simple heuristic: use first few words of user message
        new_title = " ".join(request.user_message.split()[:5])
        db_session.title = new_title
        db.commit()

    # Store the new interaction in history (ChromaDB)
    history_manager.store_chat_history(request.session_id, request.user_message, reply_text)
    
    should_generate = True
    avatar_url = None

    # 0. Check for direct category match (Keyword Search Strategy)
    # Map categories to seeded IDs
    category_map = {
        "happy": "happy_01",
        "sad": "sad_01",
        "angry": "angry_01",
        "confused": "confused_01",
        "neutral": "neutral_01"
    }
    
    if emotion_category in category_map:
        # We have a direct hit for a base emotion
        # We can verify it exists in DB or just use the known path
        # For simplicity and speed, we use the known path pattern
        avatar_url = f"http://localhost:8000/static/avatars/{category_map[emotion_category]}.png"
        should_generate = False
    else:
        # 2. Search for best matching emotion in ChromaDB (Vector Search Strategy)
        best_emotion = emotion_manager.get_best_emotion(emotion_description)
        
        if best_emotion:
            # Check threshold (adjust based on testing)
            # If distance is small enough, use existing. Else generate.
            # Increased threshold from 0.5 to 1.2 to be more lenient
            if best_emotion['distance'] < 1.2: 
                should_generate = False
                # Assuming image_path in metadata is relative like /static/avatars/happy_01.png
                avatar_url = f"http://localhost:8000{best_emotion['metadata']['image_path']}"
    
    if should_generate:
        background_tasks.add_task(generate_and_notify, request.session_id, emotion_description)
        return {
            "status": "generating_avatar",
            "reply_text": reply_text
        }
    else:
        return {
            "status": "success",
            "reply_text": reply_text,
            "avatar_url": avatar_url
        }

@app.get("/")
def read_root():
    return {"message": "Welcome to Dynamic Expressive Chatbot API"}
