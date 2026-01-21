from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re

# ---- SQLite + SQLAlchemy ----
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# ---- LangGraph ----
from langgraph.graph import StateGraph

app = FastAPI()

# -------- CORS (for React) --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- SQLite Setup --------
DATABASE_URL = "sqlite:///./crm.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# -------- DB Model --------
class InteractionModel(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String, nullable=False)
    notes = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# -------- Schemas --------
class Interaction(BaseModel):
    hcp_name: str
    notes: str

class ChatInput(BaseModel):
    text: str

# -------- LangGraph State --------
class State(dict):
    pass

def extract_entities(state: State):
    text = state["text"]

    match = re.search(r"Dr\.?\s*([A-Za-z]+)", text)

    if match:
        name = match.group(1)
        state["hcp_name"] = f"Dr. {name}"
    else:
        state["hcp_name"] = "Unknown Doctor"

    state["notes"] = text
    return state

def summarize_interaction(state: State):
    state["summary"] = f"Met {state['hcp_name']} and discussed key points."
    return state

workflow = StateGraph(State)
workflow.add_node("extract", extract_entities)
workflow.add_node("summarize", summarize_interaction)
workflow.set_entry_point("extract")
workflow.add_edge("extract", "summarize")
workflow.set_finish_point("summarize")

agent = workflow.compile()

# -------- Routes --------
@app.get("/")
def root():
    return {"message": "AI CRM Backend Running 🚀"}

@app.post("/log_interaction")
def log_interaction(data: Interaction):
    db = SessionLocal()

    record = InteractionModel(
        hcp_name=data.hcp_name,
        notes=data.notes,
        summary=f"Met {data.hcp_name}",
        created_at=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record.__dict__

@app.post("/chat_log")
def chat_log(chat: ChatInput):
    db = SessionLocal()

    try:
        result = agent.invoke({"text": chat.text})
    except Exception as e:
        result = {
            "hcp_name": "Unknown Doctor",
            "notes": chat.text,
            "summary": "AI failed — saved raw text",
        }

    record = InteractionModel(
        hcp_name=result.get("hcp_name", "Unknown Doctor"),
        notes=result.get("notes", chat.text),
        summary=result.get("summary", "No summary generated"),
        created_at=datetime.utcnow(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record.__dict__

@app.get("/interactions")
def get_interactions():
    db = SessionLocal()
    items = db.query(InteractionModel).order_by(
        InteractionModel.created_at.desc()
    ).all()

    return [i.__dict__ for i in items]

@app.delete("/interactions/{id}")
def delete_interaction(id: int):
    db = SessionLocal()
    item = db.query(InteractionModel).filter(InteractionModel.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(item)
    db.commit()
    return {"message": "Deleted successfully"}

@app.put("/interactions/{id}")
def edit_interaction(id: int, data: Interaction):
    db = SessionLocal()
    item = db.query(InteractionModel).filter(InteractionModel.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    item.hcp_name = data.hcp_name
    item.notes = data.notes
    item.summary = f"Updated: Met {data.hcp_name}"

    db.commit()
    db.refresh(item)

    return item.__dict__
