from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from langgraph.graph import StateGraph

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class Interaction(BaseModel):
    hcp_name: str
    notes: str

class ChatInput(BaseModel):
    text: str

# ---------- SQLite Database Setup ----------
def init_db():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hcp_name TEXT,
            notes TEXT,
            summary TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- LangGraph State ----------
class State(dict):
    pass

def extract_entities(state: State):
    text = state["text"]

    if "Dr." in text:
        hcp = text.split("Dr.")[1].split()[0]
        state["hcp_name"] = f"Dr. {hcp}"
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

# ---------- Helper to insert into DB ----------
def save_to_db(hcp_name, notes, summary):
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interactions (hcp_name, notes, summary, timestamp)
        VALUES (?, ?, ?, ?)
    """, (hcp_name, notes, summary, now))
    conn.commit()
    conn.close()

# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "AI CRM Backend Running 🚀"}

@app.post("/log_interaction")
def log_interaction(data: Interaction):
    summary = f"Met {data.hcp_name}"
    save_to_db(data.hcp_name, data.notes, summary)

    return {
        "hcp_name": data.hcp_name,
        "notes": data.notes,
        "summary": summary
    }

@app.post("/chat_log")
def chat_log(chat: ChatInput):
    result = agent.invoke({"text": chat.text})

    hcp_name = result.get("hcp_name", "Unknown Doctor")
    notes = result.get("notes", chat.text)
    summary = result.get("summary", "Summary generated")

    save_to_db(hcp_name, notes, summary)

    return {
        "hcp_name": hcp_name,
        "notes": notes,
        "summary": summary
    }

@app.get("/interactions")
def get_interactions():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, hcp_name, notes, summary, timestamp FROM interactions")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "hcp_name": r[1],
            "notes": r[2],
            "summary": r[3],
            "timestamp": r[4]
        })
    return data

@app.delete("/interactions/{id}")
def delete_interaction(id: int):
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM interactions WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted successfully"}
